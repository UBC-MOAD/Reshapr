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


"""Command-line interface for the extract sub-command.
"""
from pathlib import Path

import click

import reshapr.core.extract


@click.command(
    help="""
    Extract model variable time series from model products like SalishSeaCast, HRDPS & CANESM2/CGCM4.
    """,
    short_help="Extract model variable time series from model products",
)
@click.argument(
    "config_file",
    type=click.Path(
        exists=True, readable=True, file_okay=True, dir_okay=False, path_type=Path
    ),
)
@click.option(
    "--start-date",
    default="",
    help="Start date for extraction. Overrides start date in config file. Use YYYY-MM-DD format.",
)
@click.option(
    "--end-date",
    default="",
    help="End date for extraction. Overrides end date in config file. Use YYYY-MM-DD format.",
)
def extract(config_file, start_date, end_date):
    """Command-line interface for :py:func:`reshapr.core.extract.extract`.

    :param config_file: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_file: :py:class:`pathlib.Path`

    :param str start_date: Start date for extraction. Overrides start date in config file.

    :param str end_date: End date for extraction. Overrides end date in config file.
    """
    reshapr.core.extract.cli_extract(config_file, start_date, end_date)
