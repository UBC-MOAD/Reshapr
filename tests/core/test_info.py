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


"""Unit tests for core.info module.
"""
from importlib import metadata

import pytest

from reshapr.core import info


class TestInfo:
    """Unit tests for core.info.info() function.

    NOTE: These tests are a bit brittle because they rely on hard-coded line numbers in the
    captured stdout.
    """

    @pytest.mark.parametrize(
        "pkg, line", (("reshapr", 0), ("xarray", 1), ("dask", 2), ("netcdf4", 3))
    )
    def test_pkg_version(self, pkg, line, capsys):
        info.info()

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[line] == f"{pkg}, version {metadata.version(pkg)}"

    def test_cluster_configs(self, capsys):
        info.info()

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[6] == "  salish_cluster.yaml"

    def test_model_profiles(self, capsys):
        info.info()

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[9] == "  SalishSeaCast-201905.yaml"
        assert stdout_lines[10] == "  SalishSeaCast-201812.yaml"
        assert stdout_lines[11] == "  HRDPS-2.5km-GEMLAM-22sep11onward.yaml"
        assert stdout_lines[12] == "  HRDPS-2.5km-GEMLAM-pre22sep11.yaml"
        assert stdout_lines[13] == "  HRDPS-2.5km-operational.yaml"


class TestGetClusterConfigs:
    """Unit test for core.info._get_cluster_configs() function."""

    def test_get_cluster_configs(self):
        cluster_configs = info._get_cluster_configs()

        expected = ["salish_cluster.yaml"]
        assert cluster_configs == expected


class TestGetModelProfiles:
    """Unit test for core.info._get_model_profiles() function."""

    def test_get_model_profiles(self):
        model_profiles = info._get_model_profiles()

        expected = [
            "SalishSeaCast-201905.yaml",
            "SalishSeaCast-201812.yaml",
            "HRDPS-2.5km-GEMLAM-22sep11onward.yaml",
            "HRDPS-2.5km-GEMLAM-pre22sep11.yaml",
            "HRDPS-2.5km-operational.yaml",
        ]
        assert model_profiles == expected
