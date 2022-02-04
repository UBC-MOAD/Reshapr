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
    dask_client = get_dask_client(config["dask cluster"])

    start_date = arrow.get(config["start date"])
    end_date = arrow.get(config["end date"])
    log = logger.bind(
        start_date=start_date.format("YYYY-MM-DD"),
        end_date=end_date.format("YYYY-MM-DD"),
    )

    t_start = time.time()

    t_total = time.time() - t_start
    log = log.bind(t_total=t_total)
    log.info(f"total time: {t_total:.3f}s")

    dask_client.close()


def _load_config(config_file):
    """
    :param config_file: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_file: :py:class:`pathlib.Path`
    """
    log = logger.bind(config_file=os.fspath(config_file))
    try:
        with config_file.open() as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        log.error("config file not found")
        raise SystemExit(1)
    log.debug("loaded config")
    return config


## Functions below will probably eventually  be refactored into separate module(s)


def get_dask_client(dask_config):
    """Return a dask cluster client.

    If :kbd:`dask_cluster` is a dask cluster configuration YAML file,
    a :py:class:`dask.distributed.LocalCluster` is created using the parameters in the file,
    and a client connected to that cluster is returned.
    Otherwise,
    :kbd:`dask_cluster` is assumed to be the IP address and port number of an existing cluster
    in the form :kbd:`host_ip:port`,
    and a client connected to that cluster is returned.

    :param dask_config: File path and name of the YAML file to read the dask cluster configuration
                        dictionary from,
                        or a :kbd:`host_ip:port` string of an existing dask cluster fot connect to.
                        Please see :ref:`ReshaprDaskClusterYAMLFile` for details.
    :type dask_config: :py:class:`pathlib.Path` or str

    :return: Dask cluster client.
    :rtype: :py:class:`dask.distributed.Client`

    :raises: :py:exc:`SystemExit` if a client cannot be created.
    """
    log = logger.bind(dask_config=dask_config)
    try:
        # Assume config is a YAML file path
        with Path(dask_config).open("rt") as f:
            cluster_config = yaml.safe_load(f)
        log.debug("loaded dask cluster config")
    except FileNotFoundError:
        # Maybe config is a host_ip:port string
        try:
            # Connect to an existing cluster
            client = dask.distributed.Client(dask_config)
            log = log.bind(dashboard_link=client.dashboard_link)
            log.info("dask cluster dashboard")
            return client
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
