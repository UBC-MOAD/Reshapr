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


"""Extract model variable time series from model products."""
import os
import re
import sys
import time
from pathlib import Path

import arrow
import dask.distributed
import numpy
import pandas.tseries.frequencies
import structlog
import xarray
import yaml

from reshapr.utils import date_formatters

logger = structlog.get_logger()


def api_extract_netcdf(extract_config, extract_config_yaml):
    """Extract model variable(s) time series from model product to a netCDF file
     via API.

    :param dict extract_config: Extraction processing configuration dictionary.

    :param extract_config_yaml: File path and name of the YAML file that the extraction processing
                                configuration dictionary was read from.
                                Used in netCDF4 file history metadata.
    :type extract_config_yaml: :py:class:`pathlib.Path`

    :return: File path and name that netCDF4 file was written to.
    :rtype: :py:class:`pathlib.Path`
    """
    if "climatology" in extract_config and "resample" in extract_config:
        msg = "`resample` and `climatology` in the same extraction is not supported"
        logger.error(msg, config_file=os.fspath(extract_config_yaml))
        raise ValueError(msg)
    model_profile = _load_model_profile(
        Path(extract_config["dataset"]["model profile"])
    )
    ds_paths = calc_ds_paths(extract_config, model_profile)
    chunk_size = calc_ds_chunk_size(extract_config, model_profile)
    dask_client = get_dask_client(extract_config["dask cluster"])
    with open_dataset(ds_paths, chunk_size, extract_config) as ds:
        logger.info("extracting variables")
        output_coords = calc_output_coords(ds, extract_config, model_profile)
        extracted_vars = calc_extracted_vars(
            ds, output_coords, extract_config, model_profile
        )
        generated_by = f"reshapr.api.v1.extract.extract_netcdf({extract_config_yaml})"
        extracted_ds = calc_extracted_dataset(
            extracted_vars,
            output_coords,
            extract_config,
            generated_by,
        )
        if "resample" in extract_config:
            extracted_ds = _resample(extracted_ds, extract_config, model_profile)
        if "climatology" in extract_config:
            extracted_ds = _calc_climatology(
                extracted_ds, extract_config, model_profile
            )
        nc_path, encoding, nc_format, unlimited_dim = prep_netcdf_write(
            extracted_ds, output_coords, extract_config, model_profile
        )
        write_netcdf(extracted_ds, nc_path, encoding, nc_format, unlimited_dim)
    dask_client.close()
    return nc_path


def cli_extract(config_yaml, cli_start_date, cli_end_date):
    """Extract model variable time series from model product to netCDF file
    via command-line interface.

    :param config_yaml: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_yaml: :py:class:`pathlib.Path`

    :param str cli_start_date: Start date for extraction. Overrides start date in config file.

    :param str cli_end_date: End date for extraction. Overrides end date in config file.

    :raises: :py:exc:`SystemExit` if processing configuration YAML file cannot be found.
    """
    t_start = time.time()
    try:
        config = load_config(config_yaml, cli_start_date, cli_end_date)
    except FileNotFoundError:
        logger.error("config file not found", config_file=os.fspath(config_yaml))
        raise SystemExit(2)
    if "climatology" in config and "resample" in config:
        logger.error(
            "`resample` and `climatology` in the same extraction is not supported",
            config_file=os.fspath(config_yaml),
        )
        raise SystemExit(2)
    model_profile = _load_model_profile(Path(config["dataset"]["model profile"]))
    ds_paths = calc_ds_paths(config, model_profile)
    chunk_size = calc_ds_chunk_size(config, model_profile)
    dask_client = get_dask_client(config["dask cluster"])
    with open_dataset(ds_paths, chunk_size, config) as ds:
        logger.info("extracting variables")
        output_coords = calc_output_coords(ds, config, model_profile)
        extracted_vars = calc_extracted_vars(ds, output_coords, config, model_profile)
        generated_by = _reconstruct_cmd_line(config_yaml, cli_start_date, cli_end_date)
        extracted_ds = calc_extracted_dataset(
            extracted_vars,
            output_coords,
            config,
            generated_by,
            cli_start_date,
            cli_end_date,
        )
        if "resample" in config:
            extracted_ds = _resample(extracted_ds, config, model_profile)
        if "climatology" in config:
            extracted_ds = _calc_climatology(extracted_ds, config, model_profile)
        nc_path, encoding, nc_format, unlimited_dim = prep_netcdf_write(
            extracted_ds, output_coords, config, model_profile
        )
        write_netcdf(extracted_ds, nc_path, encoding, nc_format, unlimited_dim)
    logger.info("total time", t_total=time.time() - t_start)
    dask_client.close()


def load_config(config_yaml, start_date, end_date):
    """Read an extraction processing configuration YAML file and return a config dict.

    If start/end date strings ("YYYY-MM-DD") or :py:class:`arrow.arrow.Arrow` instances
    are provided, use them to override the values from the YAML file.
    An empty string or :py:obj:`None` means do not override.

    :param config_yaml: File path and name of the YAML file to read extraction processing
                        configuration dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_yaml: :py:class:`pathlib.Path`

    :param start_date: Start date for extraction. Overrides start date in config file.
    :type start_date: str or :py:obj:`None` or :py:class:`arrow.arrow.Arrow`

    :param end_date: End date for extraction. Overrides end date in config file.
    :type end_date: str or :py:obj:`None` or :py:class:`arrow.arrow.Arrow`

    :return: Extraction processing configuration dictionary.
    :rtype: dict
    """
    log = logger.bind(config_file=os.fspath(config_yaml))
    with config_yaml.open("rt") as f:
        config = yaml.safe_load(f)
    normalized_end_date = _normalize_end_date(end_date)
    config["start date"], config["end date"] = _override_start_end_date(
        config, start_date, normalized_end_date
    )
    log.info("loaded config")
    return config


def _normalize_end_date(cli_end_date):
    """
    :param str cli_end_date: End date for extraction from command-line.

    :return: Normalized end date.
    :rtype: str or :py:obj:`None`
    """
    if cli_end_date in {"", None}:
        return cli_end_date
    try:
        # Is end_date a valid date?
        arrow.get(cli_end_date)
        return cli_end_date
    except ValueError:
        # Invalid date. Assume that day value is > last day of month and change it to
        # valid last day of month.
        # This is so that we can do command-line loops like:
        #   for mm in {01..12}; do reshapr extract ... --end-date 2022-${mm}-31; done
        # without having to mess with the last day of the month.
        return (
            arrow.get(f"{cli_end_date.rsplit('-', 1)[0]}-01")
            .ceil("month")
            .format("YYYY-MM-DD")
        )


def _override_start_end_date(config, cli_start_date, cli_end_date):
    """Override config file start/end dates with those from command-line

    :param dict config: Extraction processing configuration dictionary.

    :param str cli_start_date: Start date for extraction. Overrides start date in config file.

    :param str cli_end_date: End date for extraction. Overrides end date in config file.

    :return: Possibly updated start/end dates.
    :rtype: 2-tuple
    """
    start_date = (
        config["start date"]
        if cli_start_date in {"", None}
        else arrow.get(cli_start_date).datetime.date()
    )
    end_date = (
        config["end date"]
        if cli_end_date in {"", None}
        else arrow.get(cli_end_date).datetime.date()
    )
    return start_date, end_date


def _reconstruct_cmd_line(config_yaml, cli_start_date, cli_end_date):
    """Reconstruct the command-line that was used to run the extraction.

    This is intended to be used to calculate the string to complete the "Generated by ..."
    entry in the extracted dataset history attribute.

    :param config_yaml: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_yaml: :py:class:`pathlib.Path`

    :param str cli_start_date: Start date for extraction. Overrides start date in config file.

    :param str cli_end_date: End date for extraction. Overrides end date in config file.

    :return: Reconstructed command-line.
    :rtype: str
    """
    cmd_line = f"`reshapr extract {config_yaml.absolute()}`"
    if cli_start_date:
        cmd_line = f"{cmd_line[:-1]} --start-date {cli_start_date}`"
    if cli_end_date:
        cmd_line = f"{cmd_line[:-1]} --end-date {cli_end_date}`"
    return cmd_line


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
            raise SystemExit(2)
    log.info("loaded model profile")
    results_archive = Path(model_profile["results archive"]["path"])
    log = log.bind(results_archive=os.fspath(results_archive))
    if not results_archive.exists():
        log.error("model results archive not found")
        raise SystemExit(2)
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
    days_per_file = datasets[time_base].get("days per file", 1)
    nc_files_pattern = datasets[time_base][vars_group]["file pattern"]
    log = logger.bind(
        results_archive_path=os.fspath(results_archive_path),
        time_base=time_base,
        vars_group=vars_group,
        nc_files_pattern=os.fspath(nc_files_pattern),
        days_per_file=days_per_file,
    )
    start_date = arrow.get(config["start date"])
    end_date = arrow.get(config["end date"])
    log = log.bind(
        start_date=start_date.format("YYYY-MM-DD"),
        end_date=end_date.format("YYYY-MM-DD"),
    )
    date_range = arrow.Arrow.range(
        frame=("months" if days_per_file == "month" else "days"),
        start=start_date,
        end=end_date,
    )
    ds_paths = [
        results_archive_path.joinpath(
            nc_files_pattern.format(
                ddmmmyy=date_formatters.ddmmmyy(day),
                yyyymmdd=date_formatters.yyyymmdd(day),
                yyyymm01=date_formatters.yyyymm01(day),
                yyyymm_end=date_formatters.yyyymm_end(day),
                yyyy=date_formatters.yyyy(day),
                nemo_yyyymm=date_formatters.nemo_yyyymm(day),
                nemo_yyyymmdd=date_formatters.nemo_yyyymmdd(day),
            )
        )
        for day in date_range
    ]
    log = log.bind(n_datasets=len(ds_paths))
    log.debug("collected dataset paths")
    return ds_paths


def calc_ds_chunk_size(config, model_profile):
    """Calculate chunk size dictionary for dataset loading.

    This does a transformation of the "conceptual" (time, depth, y, x) chunks dict to
    one with the correct coordinate names for the model datasets.

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Chunks size dict to use for loading model datasets.
    :rtype: dict
    """
    abstract_chunk_size = model_profile["chunk size"].copy()
    time_chunk_size = abstract_chunk_size.pop("time")
    chunk_size = {model_profile["time coord"]["name"]: time_chunk_size}
    if "depth" in abstract_chunk_size:
        depth_chunk_size = abstract_chunk_size.pop("depth")
        time_base = config["dataset"]["time base"]
        vars_group = config["dataset"]["variables group"]
        datasets = model_profile["results archive"]["datasets"]
        ds_depth_coord = datasets[time_base][vars_group]["depth coord"]
        chunk_size.update({ds_depth_coord: depth_chunk_size})
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
                             or a :kbd:`host_ip:port` string of an existing dask cluster to connect to.
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
        # Fall back to try to find cluster description in Reshapr/cluster_configs/
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
                raise SystemExit(2)
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
    config_memory_limit = cluster_config.get("memory limit", "auto")
    memory_limit = None if config_memory_limit == "None" else config_memory_limit
    cluster = dask.distributed.LocalCluster(
        name=cluster_config["name"],
        n_workers=cluster_config["number of workers"],
        threads_per_worker=cluster_config["threads per worker"],
        processes=cluster_config["processes"],
        memory_limit=memory_limit,
    )
    client = dask.distributed.Client(cluster)
    log = log.bind(dashboard_link=client.dashboard_link)
    log.info("dask cluster dashboard")
    return client


def open_dataset(ds_paths, chunk_size, config):
    """Open a list of dataset paths as a single dataset.

    This is a wrapper around :py:func:`xarray.open_mfdataset` that ensures that the
    returned dataset contains only the variable(s) of interest and their coordinates.
    That is done to minimize the memory size of the dataset.

    The returned dataset contains dask arrays that defer processing and delegate it to
    the dask cluster.

    :param list ds_paths: Dataset netCDF4 file paths in date order.

    :param dict chunk_size: Chunks size to use for loading datasets.

    :param dict config: Extraction processing configuration dictionary.

    :return: Multi-file dataset.
    :rtype: :py:class:`xarray.Dataset`

    :raises: :py:exc:`SystemExit` if multi-file dataset contains no variables.
    """
    unused_vars_yaml = (
        Path(__file__).parent.parent.parent / "model_profiles" / "unused-variables.yaml"
    )
    with unused_vars_yaml.open("rt") as f:
        unused_vars = yaml.safe_load(f)
    drop_vars = {var for var in unused_vars}
    extract_vars = {var for var in config["extract variables"]}
    # Use 1st and last dataset paths to calculate the set of all variables
    # in the dataset, and from that the set of variables to drop.
    # We need to use the variables lists from 1st and last datasets to avoid issue #51.
    for ds_path in (ds_paths[0], ds_paths[-1]):
        with xarray.open_dataset(ds_path, chunks=chunk_size, engine="h5netcdf") as ds:
            drop_vars.update(var for var in ds.data_vars)
    drop_vars -= extract_vars
    parallel_read = config.get("parallel read", True)
    ds = xarray.open_mfdataset(
        ds_paths,
        chunks=chunk_size,
        compat="override",
        coords="minimal",
        data_vars="minimal",
        drop_variables=drop_vars,
        parallel=parallel_read,
    )
    if not ds.data_vars:
        logger.error(
            "no variables in source dataset",
            extract_vars=extract_vars,
            possible_reasons="typo in variable name, or incorrect variables group",
        )
        raise SystemExit(2)
    logger.debug("opened dataset", ds=ds)
    return ds


def calc_output_coords(source_dataset, config, model_profile):
    """Construct the coordinates for the dataset containing the extracted variable(s).

    The returned coordinates container has the following mapping of attributes to
    coordinate names:

    * ``time``: ``time``
    * ``depth``: ``depth``
    * ``y_index``: ``gridY``
    * ``x_index``: ``gridX``

    except if ``extracted dataset: use model coords: True`` is set in the
    extraction configuration, in which case the output coordinates will be the same as the
    model coordinates.

    :param source_dataset: Dataset from which variables are being extracted.
    :type source_dataset: :py:class:`xarray.Dataset`

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Mapping of coordinate names to their data arrays.
    :rtype: dict
    """
    use_model_coords = config["extracted dataset"].get("use model coords", False)
    time_interval = config.get("selection", {}).get("time interval", 1)
    # stop=None in slice() means the length of the array without having to know what that is
    time_selector = {model_profile["time coord"]["name"]: slice(0, None, time_interval)}
    output_time_coord_name = (
        "time" if not use_model_coords else model_profile["time coord"]["name"]
    )
    times = create_dataarray(
        output_time_coord_name,
        source_dataset[model_profile["time coord"]["name"]].isel(time_selector),
        attrs=calc_time_coord_attrs(config["dataset"]["time base"], model_profile),
    )
    logger.debug("extraction time coordinate", time=times)

    # There are 2 special cases for which there is no depth coordinate:
    #   1. The dataset does not have a depth coordinate; e.g. HRDPS surface forcing fields
    #   2. The variable does not have a depth coordinate; e.g. sea surface height
    #      in SalishSeaCast grid_T dataset
    if "depth" not in model_profile["chunk size"]:
        # Dataset does not have a depth coordinate; e.g. HRDPS surface forcing fields
        include_depth_coord = False
        output_depth_coord_name = None
        depths = None
    else:
        datasets = model_profile["results archive"]["datasets"]
        time_base = config["dataset"]["time base"]
        vars_group = config["dataset"]["variables group"]
        depth_coord = datasets[time_base][vars_group]["depth coord"]
        include_depth_coord = any(
            [depth_coord in var.coords for var in source_dataset.data_vars.values()]
        )
        if not include_depth_coord:
            # Variable does not have a depth coordinate; e.g. sea surface height in SalishSeaCast
            # grid_T dataset
            output_depth_coord_name = None
            depths = None
        else:
            # At least 1 variable has a depth coordinate, so include depth in output dataset
            # coordinates
            depth_min = config.get("selection", {}).get("depth", {}).get("depth min", 0)
            depth_max = (
                config.get("selection", {}).get("depth", {}).get("depth max", None)
            )
            depth_interval = (
                config.get("selection", {}).get("depth", {}).get("depth interval", 1)
            )
            depth_selector = slice(depth_min, depth_max, depth_interval)
            output_depth_coord_name = "depth" if not use_model_coords else depth_coord
            depths = create_dataarray(
                output_depth_coord_name,
                source_dataset[depth_coord].isel({depth_coord: depth_selector}),
                attrs={
                    "standard_name": "sea_floor_depth",
                    "long_name": "Sea Floor Depth",
                    "units": "metres",
                    "positive": "down",
                },
            )
            logger.debug("extraction depth coordinate", depth=depths)

    y_min = config.get("selection", {}).get("grid y", {}).get("y min", 0)
    y_max = config.get("selection", {}).get("grid y", {}).get("y max", None)
    y_interval = config.get("selection", {}).get("grid y", {}).get("y interval", 1)
    y_selector = slice(y_min, y_max, y_interval)
    y_coord = model_profile["y coord"]["name"]
    output_y_coord_name = (
        "gridY" if not use_model_coords else model_profile["y coord"]["name"]
    )
    y_indices = create_dataarray(
        output_y_coord_name,
        source_dataset[y_coord].isel({y_coord: y_selector}).astype(int),
        attrs={
            "standard_name": "y",
            "long_name": "Grid Y",
            "units": model_profile["y coord"].get("units", "count"),
            "comment": model_profile["y coord"].get(
                "comment",
                f"{output_y_coord_name} values are grid indices in the model y-direction",
            ),
        },
    )
    logger.debug("extraction y coordinate", y_index=y_indices)

    x_min = config.get("selection", {}).get("grid x", {}).get("x min", 0)
    x_max = config.get("selection", {}).get("grid x", {}).get("x max", None)
    x_interval = config.get("selection", {}).get("grid x", {}).get("x interval", 1)
    x_selector = slice(x_min, x_max, x_interval)
    x_coord = model_profile["x coord"]["name"]
    output_x_coord_name = (
        "gridX" if not use_model_coords else model_profile["x coord"]["name"]
    )
    x_indices = create_dataarray(
        output_x_coord_name,
        source_dataset[x_coord].isel({x_coord: x_selector}).astype(int),
        attrs={
            "standard_name": "x",
            "long_name": "Grid X",
            "units": model_profile["x coord"].get("units", "count"),
            "comment": model_profile["x coord"].get(
                "comment",
                f"{output_x_coord_name} values are grid indices in the model x-direction",
            ),
        },
    )
    logger.debug("extraction x coordinate", x_index=x_indices)

    return (
        {
            output_time_coord_name: times,
            output_depth_coord_name: depths,
            output_y_coord_name: y_indices,
            output_x_coord_name: x_indices,
        }
        if include_depth_coord
        else {
            output_time_coord_name: times,
            output_y_coord_name: y_indices,
            output_x_coord_name: x_indices,
        }
    )


def calc_time_coord_attrs(time_base, model_profile):
    """
    :param str time_base: Time base for extraction or time interval for resampling.

    :param dict model_profile: Model profile dictionary.

    :return: Time coordinate netCDF attributes.
    :rtype: dict
    """
    extract_time_origin = model_profile["extraction time origin"]
    match time_base:
        case "hour":
            time_offset = "00:30:00"
            example = (
                "e.g. the field average values for the first hour of 8 February 2022 have "
                "a time value of 2022-02-08 00:30:00Z"
            )
        case "day":
            time_offset = "12:00:00"
            example = (
                "e.g. the field average values for 8 February 2022 have "
                "a time value of 2022-02-08 12:00:00Z"
            )
        case "month":
            time_offset = "12:00:00"
            example = (
                "e.g. the field average values for January 2022 have "
                "a time value of 2022-01-15 12:00:00Z, "
                "and those for April 2022 have a time value of 2022-04-15 00:00:00Z"
            )
        case _:
            time_offset = "00:30:00"
            example = ""
    comment = (
        "time values are UTC at the centre of the intervals over which the "
        "calculated model results are averaged"
    )
    comment = f"{comment}; {example}" if example else comment
    time_attrs = {
        "standard_name": "time",
        "long_name": "Time Axis",
        "time_origin": f"{extract_time_origin} {time_offset}",
        "comment": comment,
        # time_origin and units are provided by encoding when dataset is written to netCDF file
    }
    return time_attrs


def calc_extracted_vars(source_dataset, output_coords, config, model_profile):
    """Construct the data array for the extracted variable(s).

    :param source_dataset: Dataset from which variable(s) are being extracted.
    :type source_dataset: :py:class:`xarray.Dataset`

    :param dict output_coords: Coordinate names to data array mapping for the extracted
                               variable(s).

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Extracted variable data array(s).
    :rtype: list
    """
    time_interval = config.get("selection", {}).get("time interval", 1)
    # stop=None in slice() means the length of the array without having to know what that is
    time_selector = slice(0, None, time_interval)
    if "depth" in model_profile["chunk size"]:
        depth_min = config.get("selection", {}).get("depth", {}).get("depth min", 0)
        depth_max = config.get("selection", {}).get("depth", {}).get("depth max", None)
        depth_interval = (
            config.get("selection", {}).get("depth", {}).get("depth interval", 1)
        )
        depth_selector = slice(depth_min, depth_max, depth_interval)
        time_base = config["dataset"]["time base"]
        vars_group = config["dataset"]["variables group"]
        datasets = model_profile["results archive"]["datasets"]
        depth_coord = datasets[time_base][vars_group]["depth coord"]
        include_depth_coord = True
    else:
        depth_coord, depth_selector = None, None
        include_depth_coord = False
    y_min = config.get("selection", {}).get("grid y", {}).get("y min", 0)
    y_max = config.get("selection", {}).get("grid y", {}).get("y max", None)
    y_interval = config.get("selection", {}).get("grid y", {}).get("y interval", 1)
    y_selector = slice(y_min, y_max, y_interval)
    x_min = config.get("selection", {}).get("grid x", {}).get("x min", 0)
    x_max = config.get("selection", {}).get("grid x", {}).get("x max", None)
    x_interval = config.get("selection", {}).get("grid x", {}).get("x interval", 1)
    x_selector = slice(x_min, x_max, x_interval)
    if include_depth_coord:
        selector = {
            model_profile["time coord"]["name"]: time_selector,
            depth_coord: depth_selector,
            model_profile["y coord"]["name"]: y_selector,
            model_profile["x coord"]["name"]: x_selector,
        }
    else:
        selector = {
            model_profile["time coord"]["name"]: time_selector,
            model_profile["y coord"]["name"]: y_selector,
            model_profile["x coord"]["name"]: x_selector,
        }
    extracted_vars = []
    use_model_coords = config["extracted dataset"].get("use model coords", False)
    output_depth_coord = "depth" if not use_model_coords else depth_coord
    for name, var in source_dataset.data_vars.items():
        var_selector = (
            selector
            if depth_coord in var.coords
            else {
                c_name: c_selector
                for c_name, c_selector in selector.items()
                if c_name != depth_coord
            }
        )
        var_output_coords = (
            output_coords
            if depth_coord in var.coords
            else {
                c_name: c_selector
                for c_name, c_selector in output_coords.items()
                if c_name != output_depth_coord
            }
        )
        try:
            std_name = var.attrs["standard_name"]
        except KeyError:
            # HRDPS lacks standard_name for many vars, but has short_name
            try:
                std_name = var.attrs["short_name"]
            except KeyError:
                # Fall back to variable name as standard_name as implied by
                # https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#long-name
                std_name = name
        extracted_var = create_dataarray(
            name,
            var.isel(var_selector),
            attrs={
                "standard_name": std_name,
                "long_name": var.attrs["long_name"],
                "units": var.attrs["units"],
            },
            coords=var_output_coords,
        )
        extracted_vars.append(extracted_var)
        logger.debug(f"extracted {name}", extracted_var=extracted_var)
    if not config.get("include lons lats", False):
        return extracted_vars

    # Add longitude and latitude variables from geo ref dataset
    with xarray.open_dataset(model_profile["geo ref dataset"]["path"]) as grid_ds:
        y_coord = model_profile["geo ref dataset"]["y coord"]
        lon_var = model_profile["geo ref dataset"].get("longitude var", "longitude")
        x_coord = model_profile["geo ref dataset"]["x coord"]
        lat_var = model_profile["geo ref dataset"].get("latitude var", "latitude")
        selector = {
            y_coord: y_selector,
            x_coord: x_selector,
        }
        lons = create_dataarray(
            "longitude",
            grid_ds[lon_var].isel(selector),
            attrs={
                "standard_name": "longitude",
                "long_name": "Longitude",
                "units": "degrees_east",
            },
            coords={
                "gridY": output_coords["gridY"],
                "gridX": output_coords["gridX"],
            },
        )
        extracted_vars.append(lons)
        logger.debug(f"extracted longitudes", lons=lons)

        lats = create_dataarray(
            "latitude",
            grid_ds[lat_var].isel(selector),
            attrs={
                "standard_name": "latitude",
                "long_name": "Latitude",
                "units": "degrees_north",
            },
            coords={
                "gridY": output_coords["gridY"],
                "gridX": output_coords["gridX"],
            },
        )
        extracted_vars.append(lats)
        logger.debug(f"extracted latitudes", lats=lats)

    return extracted_vars


def create_dataarray(name, source_array, attrs, coords=None):
    """Helper function to create :py:class:`xarray.DataArray` instances.

    To create a data array to be used as a :py:class:`xarray.Dataset` coordinate,
    call without a value for :kbd:`coords`.

    To create a data array to be used as a dataset variable,
    provide the variable's coordinates dict.

    :param str name: Name of the data array.

    :param source_array: Data array from which to take the array data.
                         Also used as the coordinate values when creating a coordinate array.
    :type source_array: :py:class:`xarray.DataArray`

    :param dict attrs: Attributes of the data array.
                       These become netCDF4 variable attributes.

    :param dict coords: Coordinates of the data array.
                        Use default empty dict to create a dataset coordinate array,
                        or provide the variable's coordinates dict to create a
                        dataset variable array.

    :return: Data array for use a dataset coordinate or variable.
    :rtype: :py:class:`xarray.DataArray`
    """
    if coords is None:
        coords = {}
    return xarray.DataArray(
        name=name,
        data=source_array.data,
        coords={name: source_array.data} if coords == {} else coords,
        attrs=attrs,
    )


def calc_extracted_dataset(
    extracted_vars,
    output_coords,
    config,
    generated_by,
    override_start_date="",
    override_end_date="",
):
    """Construct the dataset of the extracted variable(s).

    :param list extracted_vars: Extracted variable data array(s).

    :param dict output_coords: Coordinate names to data array mapping for the extracted
                               variable(s).

    :param dict config: Extraction processing configuration dictionary.

    :param str generated_by: Command-line or API call string to complete "Generated by"
                             entry in dataset history attribute.

    :param str override_start_date: Extraction start date to override value in config.

    :param str override_end_date: Extraction end date to override value in config

    :return: Dataset containing extracted variable(s).
    :rtype: :py:class:`xarray.Dataset`
    """
    ds_name_root = config["extracted dataset"]["name"]
    start_date = (
        arrow.get(override_start_date)
        if override_start_date
        else arrow.get(config["start date"])
    )
    end_date = (
        arrow.get(override_end_date)
        if override_end_date
        else arrow.get(config["end date"])
    )
    ds_name = f"{ds_name_root}_{date_formatters.yyyymmdd(start_date)}_{date_formatters.yyyymmdd(end_date)}"
    ds_desc = config["extracted dataset"]["description"]
    history = f"{arrow.now('local').format('YYYY-MM-DD HH:mm ZZ')}: Generated by {generated_by}"
    extracted_ds = xarray.Dataset(
        coords=output_coords,
        data_vars={var.name: var for var in extracted_vars},
        attrs={
            "name": ds_name,
            "description": ds_desc,
            "history": history,
            "Conventions": "CF-1.6",
        },
    )
    logger.debug("extracted dataset metadata", extracted_ds=extracted_ds)
    return extracted_ds


def _resample(extracted_ds, config, model_profile):
    """
    :param extracted_ds: Dataset containing extracted variable(s).
    :type extracted_ds: :py:class:`xarray.Dataset`

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Resampled dataset containing extracted variable(s).
    :rtype: :py:class:`xarray.Dataset`
    """
    freq = config["resample"]["time interval"]
    aggregation = config["resample"].get("aggregation", "mean")
    logger.info(
        "resampling dataset", resampling_time_interval=freq, aggregation=aggregation
    )
    use_model_coords = config["extracted dataset"].get("use model coords", False)
    time_coord = "time" if not use_model_coords else model_profile["time coord"]["name"]
    # Use calendar month begin ("MS") frequency for monthly resampling so that time coordinate
    # values are the 1st days of the months.
    # They will be shifted to the middle of the months after the resampling.
    resample_freq = freq if not freq.endswith("M") else freq.replace("M", "MS")
    resampler = extracted_ds.resample(
        {time_coord: resample_freq},
        label="left",
        # There shouldn't be missing values, so don't skip them in down-sampling
        # (e.g. month-average) aggregations to force there to be missing values in result
        # dataset rather than hard to find erroneous values.
        skipna=False,
    )
    resampled_ds = getattr(resampler, aggregation)(time_coord, keep_attrs=True)
    resampled_ds[time_coord] = _calc_resampled_time_coord(
        resampled_ds.get_index(time_coord), freq
    )
    result = re.search("[MD]", freq)
    resample_quantum = result.group() if result else None
    match resample_quantum:
        case "D":
            time_base = "day"
        case "M":
            time_base = "month"
        case _:
            time_base = "unexpected"
            logger.warning(
                "unexpected resampling time interval; time coordinate metadata will be generic",
                resample_time_interval=freq,
            )
    time_attrs = getattr(resampled_ds, time_coord).attrs
    time_attrs.update(calc_time_coord_attrs(time_base, model_profile))
    logger.debug("resampled dataset metadata", resampled_ds=resampled_ds)
    return resampled_ds


def _calc_resampled_time_coord(resampled_time_index, freq):
    """
    :param :py:class:`pandas.DatetimeIndex` resampled_time_index:
    :param str freq:

    :rtype:  :py:class:`pandas.DatetimeIndex`
    """
    # pandas 2.2.0 deprecated the M, Q & Y frequency aliases in favour of ME, QE & YE
    # We interpreted M to mean MS. Now we accept both for backward compatibility.
    if not freq.endswith(("M", "MS")):
        offsets = pandas.tseries.frequencies.to_offset(freq) / 2
        return resampled_time_index + offsets
    offsets = [
        pandas.tseries.frequencies.to_offset(
            pandas.Timedelta(days=(timestamp.days_in_month / 2 - 1))
        )
        for timestamp in resampled_time_index
    ]
    return pandas.DatetimeIndex(
        [timestamp + offsets[i] for i, timestamp in enumerate(resampled_time_index)]
    )


def _calc_climatology(extracted_ds, config, model_profile):
    """
    :param :py:class:`xarray.Dataset` extracted_ds: Dataset to calculate climatology for.

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Calculated climatology dataset.
    :rtype: :py:class:`xarray.Dataset`
    """
    use_model_coords = config["extracted dataset"].get("use model coords", False)
    time_coord_name = (
        "time" if not use_model_coords else model_profile["time coord"]["name"]
    )
    climatology_time_group = config["climatology"]["group by"]
    aggregation = config["climatology"].get("aggregation", "mean")
    logger.info(
        "calculating climatology",
        groupby=climatology_time_group,
        aggregation=aggregation,
    )
    grouped_ds = extracted_ds.groupby(f"{time_coord_name}.{climatology_time_group}")
    climatology_ds = getattr(grouped_ds, aggregation)(time_coord_name)
    time_coord = getattr(climatology_ds, climatology_time_group)
    time_coord.attrs["standard_name"] = climatology_time_group
    time_coord.attrs["long_name"] = climatology_time_group.title()
    time_coord.attrs["units"] = "count"
    logger.debug("climatology dataset metadata", climatology_ds=climatology_ds)
    return climatology_ds


def calc_coord_encoding(ds, coord, config, model_profile):
    """Construct the netCDF4 encoding dictionary for a coordinate.

    :param ds: Dataset for which the ending is being constructed.
    :type ds: :py:class:`xarray.Dataset`

    :param Hashable coord: Coordinate for which the ending is being constructed.

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: netCDF4 encoding for coordinate
    :rtype: dict
    """
    match coord:
        case "time" | "time_counter":
            extract_time_origin = model_profile["extraction time origin"]
            match config["dataset"]["time base"]:
                case "day":
                    quanta = "days"
                    time_offset = "12:00:00"
                case "hour":
                    quanta = "hours"
                    time_offset = "00:30:00"
                case _:
                    quanta = "seconds"
                    time_offset = "00:30:00"
            return {
                "dtype": numpy.single,
                "units": f"{quanta} since {extract_time_origin} {time_offset}",
                "chunksizes": (1,),
                "zlib": config["extracted dataset"].get("deflate", True),
                "_FillValue": None,
            }
        case "month" | "day":
            # climatology time coordinates
            return {
                "dtype": int,
                "chunksizes": (1,),
                "zlib": config["extracted dataset"].get("deflate", True),
            }
        case "depth" | "deptht" | "depthu" | "depthv" | "depthw":
            return {
                "dtype": numpy.single,
                "chunksizes": (ds.coords[coord].size,),
                "zlib": config["extracted dataset"].get("deflate", True),
            }
        case _:
            return {
                "dtype": int,
                "chunksizes": (ds.coords[coord].size,),
                "zlib": config["extracted dataset"].get("deflate", True),
            }


def calc_var_encoding(var, output_coords, config, model_profile):
    """Construct the netCDF4 encoding dictionary for a variable.

    :param var: Variable data array.
    :type var: :py:class:`xarray.DataArray`

    :param dict output_coords: Coordinate names to data array mapping for the extracted
                               variable(s).

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: netCDF4 encoding for coordinate
    :rtype: dict
    """
    use_model_coords = config["extracted dataset"].get("use model coords", False)
    time_coord = "time" if not use_model_coords else model_profile["time coord"]["name"]
    non_time_coords = [name for name in output_coords if name != time_coord]
    if "climatology" in config:
        time_coord = config["climatology"]["group by"]
    chunksizes = []
    if time_coord in var.coords:
        chunksizes = [1]
    for name in non_time_coords:
        try:
            chunksizes.append(var.coords[name].size)
        except KeyError:
            # Handle variables that have fewer than the full set of output coordinates;
            # e.g. lons and lats that only have gridY and gridX coordinates
            pass
    return {
        "dtype": numpy.single,
        "chunksizes": tuple(chunksizes),
        "zlib": config["extracted dataset"].get("deflate", True),
    }


def prep_netcdf_write(extracted_ds, output_coords, config, model_profile):
    """Prepare parameters for :py:func:`write_netcdf` call.

    This function is separate from :py:func:`write_netcdf` to simplify unit tests.

    :param extracted_ds: Dataset containing extracted variable(s) to write to netCDF4 file.
    :type extracted_ds: :py:class:`xarray.Dataset`

    :param dict output_coords: Coordinate names to data array mapping for the extracted
                               variable(s).

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Tuple of parameters for write_netcdf();
             ``nc_path``: File path and name to write netCDF4 file to,
             ``encoding``: Encoding dict to use for netCDF4 file write,
             ``nc_format``: Format to use for netCDF4 file write.
                            Default is ``NETCDF4``.
             ``unlimited_dim``: Name of the time coordinate to set as the
                                unlimited dimension for netCDF4 file write.
    :rtype: 4-tuple
    """
    encoding = {}
    for coord in extracted_ds.coords:
        encoding[coord] = calc_coord_encoding(
            extracted_ds, coord, config, model_profile
        )
    for v_name, v_array in extracted_ds.data_vars.items():
        encoding[v_name] = calc_var_encoding(
            v_array, output_coords, config, model_profile
        )
    nc_path = Path(config["extracted dataset"]["dest dir"]) / f"{extracted_ds.name}.nc"
    nc_format = config["extracted dataset"].get("format", "NETCDF4")
    use_model_coords = config["extracted dataset"].get("use model coords", False)
    if "climatology" in config:
        # An unlimited time dimension doesn't make sense for climatology datasets
        unlimited_dim = None
    else:
        unlimited_dim = (
            "time" if not use_model_coords else model_profile["time coord"]["name"]
        )
    logger.debug(
        "prepared netCDF4 write params",
        nc_path=nc_path,
        encoding=encoding,
        nc_format=nc_format,
        unlimited_dim=unlimited_dim,
    )
    return nc_path, encoding, nc_format, unlimited_dim


def write_netcdf(extracted_ds, nc_path, encoding, nc_format, unlimited_dim):
    """Write the extracted variable(s) dataset to disk.

    This function triggers the main dask task graph execution of the extraction process.

    This function is separate from :py:func:`prep_netcdf_write` to simplify unit tests.

    :param extracted_ds: Dataset containing extracted variable(s) to write to netCDF4 file.
    :type extracted_ds: :py:class:`xarray.Dataset`

    :param nc_path: File path and name to write netCDF4 file to.
    :type nc_path: :py:class:`pathlib.Path`

    :param dict encoding: Encoding to use for netCDF4 file write.

    :param nc_format: Format to use for netCDF4 file write.
    :type nc_format: Literal["NETCDF4", "NETCDF4_CLASSIC", "NETCDF3_64BIT", "NETCDF3_CLASSIC"]

    :param str unlimited_dim: Name of the time coordinate to set as the unlimited dimension for
                              netCDF4 file write.
    """
    if unlimited_dim is None:
        extracted_ds.to_netcdf(
            nc_path,
            format=nc_format,
            encoding=encoding,
        )
    else:
        extracted_ds.to_netcdf(
            nc_path,
            format=nc_format,
            encoding=encoding,
            unlimited_dims=unlimited_dim,
            engine="netcdf4",
        )
    logger.info("wrote netCDF4 file", nc_path=os.fspath(nc_path))


# This stanza facilitates running the extract sub-command in a Python debugger
if __name__ == "__main__":  # pragma: nocover
    config_file = Path(sys.argv[1])
    try:
        idx = sys.argv.index("--start-date")
        cli_start_date = sys.argv[idx + 1]
    except ValueError:
        # No --start-date in command-line
        cli_start_date = ""
    try:
        idx = sys.argv.index("--end-date")
        cli_end_date = sys.argv[idx + 1]
    except ValueError:
        # No --end-date in command-line
        cli_end_date = ""
    cli_extract(config_file, cli_start_date, cli_end_date)
