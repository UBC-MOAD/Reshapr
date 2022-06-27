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


"""Command-line interface for the info sub-command.
"""
import click

import reshapr.core.info


@click.command(
    help="""
    Provide information about the installed Reshapr package.

    With no cluster or model profile the following information is shown:

    * versions of reshapr, xarray, dask & netcdf4 packages

    * list of dask cluster configurations included in the package

    * list of model profiles included in the package

    Specify a dask cluster configuration (e.g. `reshapr info salish_cluster`)
    or a model profile (e.g. `reshpr info SalishSeaCast-201905`) to get information
    about them.
    """,
    short_help="Provide information about dask clusters and model profiles",
)
@click.argument(
    "cluster_or_model",
    default="",
)
def info(cluster_or_model):
    """Command-line interface for :py:func:`reshapr.core.info.info`."""
    reshapr.core.info.info(cluster_or_model)
