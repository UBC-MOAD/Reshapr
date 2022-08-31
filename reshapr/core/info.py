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


"""Provide information about reshapr, dask clusters, and model profiles.
"""
import sys
from importlib import metadata
from pathlib import Path

import structlog
import xarray
import yaml
from rich.console import Console
from rich.markup import escape
from rich.padding import Padding
from rich.syntax import Syntax

CLUSTER_CONFIGS_PATH = Path(__file__).parent.parent.parent / "cluster_configs"
MODEL_PROFILES_PATH = Path(__file__).parent.parent.parent / "model_profiles"

logger = structlog.get_logger()


def info(cluster_or_model, time_interval, vars_group):
    """Provide information about reshapr, dask clusters, and model profiles."""
    console = Console()

    if cluster_or_model == "":
        _basic_info(console)
        return
    if _is_cluster(cluster_or_model):
        _cluster_info(cluster_or_model, console)
        return
    elif _is_model_profile(cluster_or_model):
        _model_profile_info(cluster_or_model, time_interval, vars_group, console)
        return
    else:
        logger.error(
            "unrecognized cluster or model profile", cluster_or_model=cluster_or_model
        )


def _basic_info(console):
    """Show info when no cluster or model profile is specified."""
    versions = {
        pkg: metadata.version(pkg) for pkg in ("reshapr", "xarray", "dask", "netcdf4")
    }
    for pkg, version in versions.items():
        console.print(f"{pkg}, version [magenta]{version}", highlight=False)

    console.print("\ndask cluster configurations included in this package:")
    cluster_configs = _get_cluster_configs()
    for cluster_config in cluster_configs:
        console.print(f"  [magenta]{cluster_config}", highlight=False)

    console.print("\nmodel profiles included in this package:")
    model_profiles = _get_model_profiles()
    for model_profile in model_profiles:
        console.print(f"  [magenta]{model_profile}", highlight=False)

    console.print(
        "\nPlease use [blue]reshapr info --help[/blue] to learn how to get deeper information,"
    )
    console.print("or [blue]reshapr --help[/blue] to learn about other sub-commands.")


def _is_cluster(cluster_or_model):
    cluster_configs = _get_cluster_configs()
    return (
        cluster_or_model in cluster_configs
        or f"{cluster_or_model}.yaml" in cluster_configs
    )


def _cluster_info(cluster, console):
    cluster = cluster if cluster.endswith(".yaml") else f"{cluster}.yaml"
    console.print(f"[green]{cluster}:")
    syntax = Syntax.from_path(CLUSTER_CONFIGS_PATH / cluster)
    console.print(Padding(syntax, (0, 2)))

    console.print(
        "\nPlease use [blue]reshapr info --help[/blue] to learn how to get other information,"
    )
    console.print("or [blue]reshapr --help[/blue] to learn about other sub-commands.")


def _is_model_profile(cluster_or_model):
    model_profiles = _get_model_profiles()
    return (
        cluster_or_model in model_profiles
        or f"{cluster_or_model}.yaml" in model_profiles
    )


def _model_profile_info(profile, time_interval, vars_group, console):
    profile_file = profile if profile.endswith(".yaml") else f"{profile}.yaml"
    console.print(f"[green]{profile_file}:", highlight=False)
    with (MODEL_PROFILES_PATH / profile_file).open("rt") as f:
        model_profile = yaml.safe_load(f)

    if time_interval and vars_group:
        _vars_list(model_profile, time_interval, vars_group, console)
        return
    if time_interval or vars_group:
        logger.error(
            "both time interval and variable group are required",
            time_interval=time_interval,
            vars_group=vars_group,
        )
        return

    console.print(
        "[cyan]variable groups[/cyan] from [magenta]time intervals[/magenta] in this model:"
    )
    datasets = model_profile["results archive"]["datasets"]
    for time_base in datasets:
        console.print(f"  [magenta]{time_base}")
        for vars_group in datasets[time_base]:
            console.print(f"    [cyan]{vars_group}")

    console.print(
        "\nPlease use [blue]reshapr info model-profile time-interval variable-group[/blue]\n"
        "(e.g. [blue]reshapr info SalishSeaCast-201905 hour biology[/blue])\n"
        "to get the list of variables in a [cyan]variable group[/cyan].",
        highlight=False,
    )
    console.print(
        "\nPlease use [blue]reshapr info --help[/blue] to learn how to get other information,"
    )
    console.print("or [blue]reshapr --help[/blue] to learn about other sub-commands.")


def _vars_list(model_profile, time_interval, vars_group, console):
    unused_vars_yaml = (
        Path(__file__).parent.parent.parent / "model_profiles" / "unused-variables.yaml"
    )
    with unused_vars_yaml.open("rt") as f:
        unused_vars = yaml.safe_load(f)
    drop_vars = {var for var in unused_vars}
    results_archive_path = Path(model_profile["results archive"]["path"])
    datasets = model_profile["results archive"]["datasets"]
    try:
        vars_groups = datasets[time_interval]
    except KeyError:
        logger.error(
            "time interval is not in model profile", time_interval=time_interval
        )
        return
    try:
        dataset = vars_groups[vars_group]
    except KeyError:
        logger.error("variables group is not in model profile", vars_group=vars_group)
        return
    nc_files_pattern = dataset["file pattern"].format(
        ddmmmyy="*",
        yyyymmdd="*",
        nemo_yyyymm="*",
        nemo_yyyymmdd="*",
    )
    ds_path = next(results_archive_path.glob(nc_files_pattern))
    console.print(
        f"[magenta]{time_interval}[/magenta]-averaged variables in [cyan]{vars_group}[/cyan] group:"
    )
    with xarray.open_dataset(ds_path, drop_variables=drop_vars) as ds:
        for var in ds.data_vars:
            long_name = ds[var].attrs["long_name"]
            units = f"[{ds[var].attrs['units']}]"
            console.print(
                f"  - [red]{var}[/red] : {long_name} {escape(units)}", highlight=False
            )

    console.print(
        "\nPlease use [blue]reshapr info --help[/blue] to learn how to get other information,"
    )
    console.print("or [blue]reshapr --help[/blue] to learn about other sub-commands.")


def _get_cluster_configs():
    cluster_configs = [
        config.name
        for config in CLUSTER_CONFIGS_PATH.glob("*.yaml")
        if config.name != "unit_test_cluster.yaml"
    ]
    return cluster_configs


def _get_model_profiles():
    model_profiles = [
        profile.name
        for profile in MODEL_PROFILES_PATH.glob("*.yaml")
        if profile.name != "unused-variables.yaml"
    ]
    return model_profiles


# This stanza facilitates running the info sub-command in a Python debugger
if __name__ == "__main__":  # pragma: nocover
    cluster_or_model, time_interval, var_group = "", "", ""
    try:
        cluster_or_model = sys.argv[1]
    except IndexError:
        pass
    try:
        time_interval = sys.argv[2]
    except IndexError:
        pass
    try:
        var_group = " ".join(sys.argv[3:])
    except IndexError:
        pass
    info(cluster_or_model, time_interval, var_group)
