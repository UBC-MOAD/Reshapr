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
from importlib import metadata

from rich.console import Console


def info():
    """Provide information about dask clusters and model profiles."""
    console = Console()

    versions = {
        pkg: metadata.version(pkg) for pkg in ("reshapr", "xarray", "dask", "netcdf4")
    }
    for pkg, version in versions.items():
        console.print(f"{pkg}, version [magenta]{version}")


# This stanza facilitates running the info sub-command in a Python debugger
if __name__ == "__main__":
    info()
