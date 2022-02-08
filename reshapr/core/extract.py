# Copyright 2022 – present, UBC EOAS MOAD Group and The University of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# SPDX-License-Identifier: Apache-2.0


"""Extract model variable time series from model products.
"""
import os
import sys
import time
from pathlib import Path

import arrow
import dask.distributed
import structlog
import yaml

logger = structlog.get_logger()


def extract(config_file):
    """Extract model variable time series from model products.

    :param config_file: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_file: :py:class:`pathlib.Path`
    """
    config = _load_config(config_file)
    model_profile = _load_model_profile(Path(config["dataset"]["model profile"]))
    ds_paths = calc_ds_paths(config, model_profile)
    chunk_size = calc_ds_chunk_size(config, model_profile)

    dask_client = get_dask_client(config["dask cluster"])

    t_start = time.time()

    t_total = time.time() - t_start
    log = logger.bind(t_total=t_total)
    log.info(f"total time: {t_total:.3f}s")

    dask_client.close()


def _load_config(config_yaml):
    """
    :param config_yaml: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_yaml: :py:class:`pathlib.Path`

    :return: Extraction processing configuration dictionary.
    :rtype: dict

    :raises: :py:exc:`SystemExit` if processing configuration YAML file cannot be opened.
    """
    log = logger.bind(config_file=os.fspath(config_yaml))
    try:
        with config_yaml.open("rt") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        log.error("config file not found")
        raise SystemExit(1)
    log.debug("loaded config")
    return config


def _load_model_profile(model_profile_yaml):
    """
    :param model_profile_yaml: File path and name of the YAML file to read model profile
                               dictionary from.
                               Please see :ref:`ReshaprModelProfileYAMLFile` for details.
    :type model_profile_yaml: :py:class:`pathlib.Path`

    :return: Model profile dictionary.
    :rtype: dict

    :raises: :py:exc:`SystemExit` if model profile YAML file cannot be opened,
             or if the model results archive path in the file cannot be accessed.
    """
    log = logger.bind(model_profile_yaml=os.fspath(model_profile_yaml))
    try:
        # Handle possible user-created model profile
        with model_profile_yaml.open("rt") as f:
            model_profile = yaml.safe_load(f)
    except FileNotFoundError:
        # Fall back to try to find model profile in Reshapr/model_profiles/
        model_profiles_path = Path(__file__).parent.parent.parent / "model_profiles"
        try:
            log = logger.bind(
                model_profile_yaml=os.fspath(model_profiles_path / model_profile_yaml)
            )
            with (model_profiles_path / model_profile_yaml).open("rt") as f:
                model_profile = yaml.safe_load(f)
        except FileNotFoundError:
            log.error("model profile file not found")
            raise SystemExit(1)
    log.debug("loaded model profile")
    results_archive = Path(model_profile["results archive"]["path"])
    log = log.bind(results_archive=os.fspath(results_archive))
    if not results_archive.exists():
        log.error("model results archive not found")
        raise SystemExit(1)
    return model_profile


def calc_ds_paths(config, model_profile):
    """Calculate the list of dataset netCDF4 file paths to process.

    The list is in order ascending date order.

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Dataset netCDF4 file paths in date order.
    :rtype: list
    """
    results_archive_path = Path(model_profile["results archive"]["path"])
    time_base = config["dataset"]["time base"]
    vars_group = config["dataset"]["variables group"]
    datasets = model_profile["results archive"]["datasets"]
    nc_files_pattern = datasets[time_base][vars_group]["file pattern"]
    log = logger.bind(
        results_archive_path=os.fspath(results_archive_path),
        time_base=time_base,
        vars_group=vars_group,
        nc_files_pattern=nc_files_pattern,
    )
    start_date = arrow.get(config["start date"])
    end_date = arrow.get(config["end date"])
    log = log.bind(
        start_date=start_date.format("YYYY-MM-DD"),
        end_date=end_date.format("YYYY-MM-DD"),
    )
    date_range = arrow.Arrow.range("days", start_date, end_date)
    ds_paths = [
        results_archive_path
        / ddmmmyy(day)
        / nc_files_pattern.format(yyyymmdd=yyyymmdd(day))
        for day in date_range
    ]
    log = log.bind(n_datasets=len(ds_paths))
    log.debug("collected dataset paths")
    return ds_paths


def ddmmmyy(arrow_date):
    """Return an Arrow date as a string formatted as lower-cased `ddmmmyy`.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as lower-cased `ddmmmyy`.
    :rtype: str
    """
    return arrow_date.format("DDMMMYY").lower()


def yyyymmdd(arrow_date):
    """Return an Arrow date as a string of digits formatted as `yyyymmdd`.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as `yyyymmdd` digits.
    :rtype: str
    """
    return arrow_date.format("YYYYMMDD").lower()


def calc_ds_chunk_size(config, model_profile):
    """Calculate chunk size dictionary for dataset loading.

    This does a transformation of the "conceptual" (time, depth, y, x) chunks dict to
    one with the correct coordinate names for the model datasets.

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Chunks size dict to use for loading model datasets.
    :rtype: dict
    """
    abstract_chunk_size = model_profile["chunk size"]
    time_chunk_size = abstract_chunk_size.pop("time")
    depth_chunk_size = abstract_chunk_size.pop("depth")
    time_base = config["dataset"]["time base"]
    vars_group = config["dataset"]["variables group"]
    datasets = model_profile["results archive"]["datasets"]
    ds_depth_coord = datasets[time_base][vars_group]["depth coord"]
    chunk_size = {
        model_profile["time coord"]: time_chunk_size,
        ds_depth_coord: depth_chunk_size,
    }
    chunk_size.update(abstract_chunk_size)
    logger.debug("chunk size for dataset loading", chunk_size=chunk_size)
    return chunk_size


def get_dask_client(dask_config_yaml):
    """Return a dask cluster client.

    If :kbd:`dask_cluster` is a dask cluster configuration YAML file,
    a :py:class:`dask.distributed.LocalCluster` is created using the parameters in the file,
    and a client connected to that cluster is returned.
    Otherwise,
    :kbd:`dask_cluster` is assumed to be the IP address and port number of an existing cluster
    in the form :kbd:`host_ip:port`,
    and a client connected to that cluster is returned.

    :param dask_config_yaml: File path and name of the YAML file to read the dask cluster configuration
                             dictionary from,
                             or a :kbd:`host_ip:port` string of an existing dask cluster fot connect to.
                             Please see :ref:`ReshaprDaskClusterYAMLFile` for details.
    :type dask_config_yaml: :py:class:`pathlib.Path` or str

    :return: Dask cluster client.
    :rtype: :py:class:`dask.distributed.Client`

    :raises: :py:exc:`SystemExit` if a client cannot be created.
    """
    log = logger.bind(dask_config_yaml=os.fspath(dask_config_yaml))
    try:
        # Handle possible user-created dask cluster description
        with Path(dask_config_yaml).open("rt") as f:
            cluster_config = yaml.safe_load(f)
    except FileNotFoundError:
        # Fall back to try to find model profile in Reshapr/model_profiles/
        cluster_configs_path = Path(__file__).parent.parent.parent / "cluster_configs"
        try:
            with Path(cluster_configs_path / dask_config_yaml).open("rt") as f:
                cluster_config = yaml.safe_load(f)
            log = logger.bind(
                dask_config_yaml=os.fspath(cluster_configs_path / dask_config_yaml)
            )
        except FileNotFoundError:
            # Maybe config is a host_ip:port string
            try:
                # Connect to an existing cluster
                client = dask.distributed.Client(dask_config_yaml)
                log = log.bind(dashboard_link=client.dashboard_link)
                log.info("dask cluster dashboard")
                return client
            except TypeError:
                log.error("dask cluster config file not found")
                raise SystemExit(1)
            except ValueError:
                log.error(
                    "unrecognized dask cluster config; expected YAML file path or host_ip:port"
                )
                raise SystemExit(1)
            except OSError:
                log.error(
                    "requested dask cluster is not running or refused your connection"
                )
                raise SystemExit(1)
    log.debug("loaded dask cluster config")
    # Set up cluster described in YAML file
    cluster = dask.distributed.LocalCluster(
        name=cluster_config["name"],
        n_workers=cluster_config["number of workers"],
        threads_per_worker=cluster_config["threads per worker"],
        processes=cluster_config["processes"],
    )
    client = dask.distributed.Client(cluster)
    log = log.bind(dashboard_link=client.dashboard_link)
    log.info("dask cluster dashboard")
    return client


# This stanza facilitates running the extract sub-command in a Python debugger
if __name__ == "__main__":
    config_file = Path(sys.argv[1])
    extract(config_file)
