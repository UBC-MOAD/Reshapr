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


"""Command-line interface setup and sub-commands registry.
"""
import logging

import click
import structlog

from reshapr.cli.extract import extract
from reshapr.cli.info import info


@click.group(
    help="""
    Reshape model variable arrays from model products like SalishSeaCast, HRDPS & CANESM2/CGCM4.
    """
)
@click.version_option()
@click.option(
    "-v",
    "--verbosity",
    default="info",
    show_default=True,
    type=click.Choice(("debug", "info", "warning", "error", "critical")),
    help="""
    Choose how much information you want to see about the progress of the process;
    warning, error, and critical should be silent unless something bad goes wrong.
    """,
)
def reshapr(verbosity):
    """Click commands group into which sub-commands must be registered.

    :param str verbosity: Verbosity level of logging messages about the progress of the process.
                          Choices are :kbd:`debug, info, warning, error, critical`.
                          :kbd:`warning`, :kbd:`error`, and :kbd:`critical` should be silent
                          unless something bad goes wrong.
                          Default is :kbd:`info`.
    """
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            min_level=getattr(logging, verbosity.upper())
        )
    )


reshapr.add_command(extract)
reshapr.add_command(info)
