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
import numpy
import structlog
import xarray
import yaml

logger = structlog.get_logger()


def extract(config_file, start_date, end_date):
    """Extract model variable time series from model products.

    :param config_file: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_file: :py:class:`pathlib.Path`

    :param str start_date: Start date for extraction. Overrides start date in config file.

    :param str end_date: End date for extraction. Overrides end date in config file.
    """
    t_start = time.time()
    config = _load_config(config_file)
    end_date = _normalize_end_date(end_date)
    config["start date"], config["end date"] = _override_start_end_date(
        config, start_date, end_date
    )
    model_profile = _load_model_profile(Path(config["dataset"]["model profile"]))
    ds_paths = calc_ds_paths(config, model_profile)
    chunk_size = calc_ds_chunk_size(config, model_profile)
    dask_client = get_dask_client(config["dask cluster"])
    with open_dataset(ds_paths, chunk_size, config, model_profile) as ds:
        logger.info("extracting variables")
        output_coords = calc_output_coords(ds, config, model_profile)
        extracted_vars = calc_extracted_vars(ds, output_coords, config, model_profile)
        extracted_ds = calc_extracted_dataset(
            extracted_vars, output_coords, config, config_file, start_date, end_date
        )
        if "resample" in config:
            extracted_ds = _resample(extracted_ds, config, model_profile)
        nc_path, encoding, nc_format = prep_netcdf_write(
            extracted_ds, output_coords, config, model_profile
        )
        write_netcdf(extracted_ds, nc_path, encoding, nc_format)
    logger.info("total time", t_total=time.time() - t_start)
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
        raise SystemExit(2)
    log.info("loaded config")
    return config


def _normalize_end_date(end_date):
    """
    :param str end_date: End date for extraction from command-line.

    :return: Normalized end date.
    :rtype: str
    """
    if end_date == "":
        return end_date
    try:
        # Is end_date a valid date?
        arrow.get(end_date)
        return end_date
    except ValueError:
        # Invalid date. Assume that day value is > last day of month and change it to
        # valid last day of month.
        # This is so that we can do command-line loops like:
        #   for mm in {01..12}; do reshapr extract ... --end-date 2022-${mm}-31; done
        # without having to mess with the last day of the month.
        return (
            arrow.get(f"{end_date.rsplit('-', 1)[0]}-01")
            .ceil("month")
            .format("YYYY-MM-DD")
        )


def _override_start_end_date(config, start_date, end_date):
    """Override config file start/end dates with those from command-line

    :param dict config: Extraction processing configuration dictionary.

    :param str start_date: Start date for extraction. Overrides start date in config file.

    :param str end_date: End date for extraction. Overrides end date in config file.

    :return: Possibly updated Extraction processing configuration dictionary.
    :rtype: dict
    """
    return start_date or config["start date"], end_date or config["end date"]


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
    nc_files_pattern = datasets[time_base][vars_group]["file pattern"]
    log = logger.bind(
        results_archive_path=os.fspath(results_archive_path),
        time_base=time_base,
        vars_group=vars_group,
        nc_files_pattern=os.fspath(nc_files_pattern),
    )
    start_date = arrow.get(config["start date"])
    end_date = arrow.get(config["end date"])
    log = log.bind(
        start_date=start_date.format("YYYY-MM-DD"),
        end_date=end_date.format("YYYY-MM-DD"),
    )
    date_range = arrow.Arrow.range("days", start_date, end_date)
    ds_paths = [
        results_archive_path.joinpath(
            nc_files_pattern.format(
                ddmmmyy=ddmmmyy(day),
                yyyymmdd=yyyymmdd(day),
                nemo_yyyymmdd=nemo_yyyymmdd(day),
            )
        )
        for day in date_range
    ]
    log = log.bind(n_datasets=len(ds_paths))
    log.debug("collected dataset paths")
    return ds_paths


def ddmmmyy(arrow_date):
    """Return an Arrow date as a string formatted as lower-cased `ddmmmyy`; e.g. 28feb22.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as lower-cased `ddmmmyy`.
    :rtype: str
    """
    return arrow_date.format("DDMMMYY").lower()


def yyyymmdd(arrow_date):
    """Return an Arrow date as a string of digits formatted as `yyyymmdd`; e.g. 20020228.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as `yyyymmdd` digits.
    :rtype: str
    """
    return arrow_date.format("YYYYMMDD").lower()


def nemo_yyyymmdd(arrow_date):
    """Return an Arrow date as a string formatted using the NEMO forcing date convention;
    i.e. y2022m02d28.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as NEMO forcing date.
    :rtype: str
    """
    return arrow_date.format("[y]YYYY[m]MM[d]DD")


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


def open_dataset(ds_paths, chunk_size, config, model_profile):
    """Open a list of dataset paths as a single dataset.

    This is a wrapper around :py:func:`xarray.open_mfdataset` that ensures that the
    returned dataset contains only the variable(s) of interest and their coordinates.
    That is done to minimize the memory size of the dataset.

    The returned dataset contains dask arrays that defer processing and delegate it to
    the dask cluster.

    :param list ds_paths: Dataset netCDF4 file paths in date order.

    :param dict chunk_size: Chunks size to use for loading datasets.

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Multi-file dataset.
    :rtype: :py:class:`xarray.Dataset`
    """
    unused_vars_yaml = (
        Path(__file__).parent.parent.parent / "model_profiles" / "unused-variables.yaml"
    )
    with unused_vars_yaml.open("rt") as f:
        unused_vars = yaml.safe_load(f)
    drop_vars = {var for var in unused_vars}
    extract_vars = {var for var in config["extract variables"]}
    # Use 1st dataset path to calculate the set of variables to drop
    with xarray.open_dataset(ds_paths[0], chunks=chunk_size) as ds:
        drop_vars.update(var for var in ds.data_vars)
    drop_vars -= extract_vars
    ds = xarray.open_mfdataset(
        ds_paths,
        chunks=chunk_size,
        compat="override",
        coords="minimal",
        data_vars="minimal",
        drop_variables=drop_vars,
        parallel=True,
    )
    logger.debug("opened dataset", ds=ds)
    return ds


def calc_output_coords(source_dataset, config, model_profile):
    """Construct the coordinates for the dataset containing the extracted variable(s).

    The returned coordinates container has the following mapping of attributes to
    coordinate names:

    * :kbd:`time`: :kbd:`time`
    * :kbd:`depth`: :kbd:`depth`
    * :kbd:`y_index`: :kbd:`gridY`
    * :kbd:`x_index`: :kbd:`gridx`

    :param source_dataset: Dataset from which variables are being extracted.
    :type source_dataset: :py:class:`xarray.Dataset`

    :param dict config: Extraction processing configuration dictionary.

    :param dict model_profile: Model profile dictionary.

    :return: Mapping of coordinate names to their data arrays.
    :rtype: dict
    """
    time_interval = config.get("selection", {}).get("time interval", 1)
    # stop=None in slice() means the length of the array without having to know what that is
    time_selector = {model_profile["time coord"]["name"]: slice(0, None, time_interval)}
    times = create_dataarray(
        "time",
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
            depths = create_dataarray(
                "depth",
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
    y_indices = create_dataarray(
        "gridY",
        source_dataset[y_coord].isel({y_coord: y_selector}).astype(int),
        attrs={
            "standard_name": "y",
            "long_name": "Grid Y",
            "units": model_profile["y coord"].get("units", "count"),
            "comment": model_profile["y coord"].get(
                "comment", "gridY values are grid indices in the model y-direction"
            ),
        },
    )
    logger.debug("extraction y coordinate", y_index=y_indices)

    x_min = config.get("selection", {}).get("grid x", {}).get("x min", 0)
    x_max = config.get("selection", {}).get("grid x", {}).get("x max", None)
    x_interval = config.get("selection", {}).get("grid x", {}).get("x interval", 1)
    x_selector = slice(x_min, x_max, x_interval)
    x_coord = model_profile["x coord"]["name"]
    x_indices = create_dataarray(
        "gridX",
        source_dataset[x_coord].isel({x_coord: x_selector}).astype(int),
        attrs={
            "standard_name": "x",
            "long_name": "Grid X",
            "units": model_profile["x coord"].get("units", "count"),
            "comment": model_profile["x coord"].get(
                "comment", "gridX values are grid indices in the model x-direction"
            ),
        },
    )
    logger.debug("extraction x coordinate", x_index=x_indices)

    return (
        {"time": times, "depth": depths, "gridY": y_indices, "gridX": x_indices}
        if include_depth_coord
        else {"time": times, "gridY": y_indices, "gridX": x_indices}
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
                if c_name != "depth"
            }
        )
        try:
            std_name = var.attrs["standard_name"]
        except KeyError:
            # HRDPS lacks standard_name for many vars, but has short_name
            std_name = var.attrs["short_name"]
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
    extracted_vars, output_coords, config, config_yaml, cli_start_date, cli_end_date
):
    """Construct the dataset of the extracted variable(s).

    :param list extracted_vars: Extracted variable data array(s).

    :param dict output_coords: Coordinate names to data array mapping for the extracted
                               variable(s).

    :param dict config: Extraction processing configuration dictionary.

    :param config_yaml: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_yaml: :py:class:`pathlib.Path`

    :param str cli_start_date: Start date for extraction from command-line.

    :param str cli_end_date: End date for extraction from command-line.

    :return: Dataset containing extracted variable(s).
    :rtype: :py:class:`xarray.Dataset`
    """
    ds_name_root = config["extracted dataset"]["name"]
    start_date = arrow.get(config["start date"])
    end_date = arrow.get(config["end date"])
    ds_name = f"{ds_name_root}_{yyyymmdd(start_date)}_{yyyymmdd(end_date)}"
    ds_desc = config["extracted dataset"]["description"]
    history = (
        f"{arrow.now('PST').format('YYYY-MM-DD HH:mm')}: "
        f"Generated by `reshapr extract {config_yaml.absolute()}`"
    )
    if cli_start_date or cli_end_date:
        history = (
            f"{history[:-1]} --start-date {cli_start_date} --end-date {cli_end_date}`"
        )
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
    start_date = arrow.get(config["start date"])
    end_date = arrow.get(config["end date"])
    resampler = extracted_ds.resample(
        time=freq,
        label="left",
        loffset=(end_date.shift(days=+1) - start_date) / 2,
        # There shouldn't be missing values, so don't skip them in down-sampling
        # (e.g. month-average) aggregations to force there to be missing values in result
        # dataset rather than hard to find erroneous values.
        skipna=False,
    )
    resampled_ds = getattr(resampler, aggregation)("time", keep_attrs=True)
    if freq.endswith("M"):
        time_base = "month"
    else:
        time_base = "unexpected"
        logger.warning(
            "unexpected resampling time interval; time coordinate metadata will be generic",
            resample_time_interval=freq,
        )
    resampled_ds.time.attrs.update(calc_time_coord_attrs(time_base, model_profile))
    logger.debug("resampled dataset metadata", resampled_ds=resampled_ds)
    return resampled_ds


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
        case "time":
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
        case "depth":
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


def calc_var_encoding(var, output_coords, config):
    """Construct the netCDF4 encoding dictionary for a variable.

    :param var: Variable data array.
    :type var: :py:class:`xarray.DataArray`

    :param dict output_coords: Coordinate names to data array mapping for the extracted
                               variable(s).

    :param dict config: Extraction processing configuration dictionary.

    :return: netCDF4 encoding for coordinate
    :rtype: dict
    """
    chunksizes = []
    for name in output_coords:
        try:
            chunksizes.append(var.coords[name].size)
        except KeyError:
            # Handle variables that have fewer than the full set of output coordinates;
            # e.g. lons and lats that only have gridY and gridX coordinates
            pass
    if "time" in var.coords:
        chunksizes[0] = 1
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
             :kbd:`nc_path`: File path and name to write netCDF4 file to,
             :kbd:`encoding`: Encoding dict to use for netCDF4 file write,
             :kbd:`nc_format`: Format to use for netCDF4 file write.
                               Defaults to kbd:`NETCDF4`.
    :rtype: 3-tuple
    """
    encoding = {}
    for coord in extracted_ds.coords:
        encoding[coord] = calc_coord_encoding(
            extracted_ds, coord, config, model_profile
        )
    for v_name, v_array in extracted_ds.data_vars.items():
        encoding[v_name] = calc_var_encoding(v_array, output_coords, config)
    nc_path = Path(config["extracted dataset"]["dest dir"]) / f"{extracted_ds.name}.nc"
    nc_format = config["extracted dataset"].get("format", "NETCDF4")
    logger.debug(
        "prepared netCDF4 write params",
        nc_path=nc_path,
        encoding=encoding,
        nc_format=nc_format,
    )
    return nc_path, encoding, nc_format


def write_netcdf(extracted_ds, nc_path, encoding, nc_format):
    """WRite the extracted variable(s) dataset to disk.

    This function triggers the main dask task graph execution of the extraction process.

    This function is separate from :py:func:`prep_netcdf_write` to simplify unit tests.

    :param extracted_ds: Dataset containing extracted variable(s) to write to netCDF4 file.
    :type extracted_ds: :py:class:`xarray.Dataset`

    :param nc_path: File path and name to write netCDF4 file to.
    :type nc_path: :py:class:`pathlib.Path`

    :param dict encoding: Encoding to use for netCDF4 file write.

    :param str nc_format: Format to use for netCDF4 file write.
    """
    extracted_ds.to_netcdf(
        nc_path,
        format=nc_format,
        encoding=encoding,
        unlimited_dims="time",
    )
    logger.info("wrote netCDF4 file", nc_path=os.fspath(nc_path))


# This stanza facilitates running the extract sub-command in a Python debugger
if __name__ == "__main__":  # pragma: nocover
    config_file = Path(sys.argv[1])
    try:
        idx = sys.argv.index("--start-date")
        start_date = sys.argv[idx + 1]
    except ValueError:
        # No --start-date in command-line
        start_date = ""
    try:
        idx = sys.argv.index("--end-date")
        end_date = sys.argv[idx + 1]
    except ValueError:
        # No --end-date in command-line
        end_date = ""
    extract(config_file, start_date, end_date)
