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
import yaml
from rich.console import Console
from rich.padding import Padding
from rich.syntax import Syntax

CLUSTER_CONFIGS_PATH = Path(__file__).parent.parent.parent / "cluster_configs"
MODEL_PROFILES_PATH = Path(__file__).parent.parent.parent / "model_profiles"

logger = structlog.get_logger()


def info(cluster_or_model):
    """Provide information about reshapr, dask clusters, and model profiles."""
    console = Console()

    if cluster_or_model == "":
        _basic_info(console)
        return
    if _is_cluster(cluster_or_model):
        _cluster_info(cluster_or_model, console)
        return
    elif _is_model_profile(cluster_or_model):
        _model_profile_info(cluster_or_model, console)
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
        console.print(f"{pkg}, version [magenta]{version}")

    console.print("\ndask cluster configurations included in this package:")
    cluster_configs = _get_cluster_configs()
    for cluster_config in cluster_configs:
        console.print(f"  [magenta]{cluster_config}")

    console.print("\nmodel profiles included in this package:")
    model_profiles = _get_model_profiles()
    for model_profile in model_profiles:
        console.print(f"  [magenta]{model_profile}")

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


def _model_profile_info(profile, console):
    profile_file = profile if profile.endswith(".yaml") else f"{profile}.yaml"
    console.print(f"[green]{profile_file}:", highlight=False)
    with (MODEL_PROFILES_PATH / profile_file).open("rt") as f:
        model_profile = yaml.safe_load(f)

    console.print(
        "[cyan]variable groups[/cyan] from [magenta]time intervals[/magenta] in this model:"
    )
    datasets = model_profile["results archive"]["datasets"]
    for time_base in datasets:
        console.print(f"  [magenta]{time_base}")
        var_groups = datasets[time_base]
        for var_group in var_groups:
            console.print(f"    [cyan]{var_group}")

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
    try:
        cluster_or_model = sys.argv[1]
    except IndexError:
        cluster_or_model = ""
    info(cluster_or_model)
