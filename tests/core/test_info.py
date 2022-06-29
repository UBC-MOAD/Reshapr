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
import textwrap
from importlib import metadata

import pytest

from reshapr.core import info


class TestBasicInfo:
    """Unit tests for core.info.info() function with empty cluster_or_model argument.

    NOTE: These tests are a bit brittle because they rely on hard-coded line numbers in the
    captured stdout.
    """

    @pytest.mark.parametrize(
        "pkg, line", (("reshapr", 0), ("xarray", 1), ("dask", 2), ("netcdf4", 3))
    )
    def test_pkg_version(self, pkg, line, capsys):
        info.info(cluster_or_model="")

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[line] == f"{pkg}, version {metadata.version(pkg)}"

    def test_cluster_configs(self, capsys):
        info.info(cluster_or_model="")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = {"salish_cluster.yaml"}
        assert set(line.strip() for line in stdout_lines[6:7]) == expected

    def test_model_profiles(self, capsys):
        info.info(cluster_or_model="")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = {
            "SalishSeaCast-201905.yaml",
            "SalishSeaCast-201812.yaml",
            "HRDPS-2.5km-GEMLAM-22sep11onward.yaml",
            "HRDPS-2.5km-GEMLAM-pre22sep11.yaml",
            "HRDPS-2.5km-operational.yaml",
        }
        assert (
            set(line.strip() for line in stdout_lines[9 : len(expected) + 9])
            == expected
        )


class TestIsCluster:
    """Unit tests for core.info._is_cluster() function."""

    @pytest.mark.parametrize(
        "cluster, expected",
        (
            ("salish_cluster", True),
            ("salish_cluster.yaml", True),
            ("foo", False),
        ),
    )
    def test_is_cluster(self, cluster, expected):
        is_cluster = info._is_cluster(cluster)

        assert is_cluster is expected


class TestClusterInfo:
    """Unit tests for core.info.info() function with cluster as argument.

    NOTE: These tests are a bit brittle because they rely on hard-coded line numbers in the
    captured stdout.
    """

    @pytest.mark.parametrize(
        "cluster, expected",
        (
            ("salish_cluster", "salish_cluster.yaml:"),
            ("salish_cluster.yaml", "salish_cluster.yaml:"),
        ),
    )
    def test_cluster_file_name(self, cluster, expected, capsys):
        info.info(cluster)

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[0] == expected

    def test_cluster_file_contents(self, capsys):
        info.info("salish_cluster.yaml")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = textwrap.dedent(
            """\
                # Configuration for a dask cluster on salish

                name: salish dask cluster
                processes: True
                number of workers: 4
                threads per worker: 4
            """
        ).splitlines()
        assert [line.strip() for line in stdout_lines[1:7]] == expected


class TestIsModelProfile:
    """Unit tests for core.info._is_model_profile() function."""

    @pytest.mark.parametrize(
        "model_profile, expected",
        (
            ("SalishSeaCast-201905", True),
            ("SalishSeaCast-201905.yaml", True),
            ("foo", False),
        ),
    )
    def test_is_model_profile(self, model_profile, expected):
        is_profile = info._is_model_profile(model_profile)

        assert is_profile is expected


class TestModelProfileInfo:
    """Unit tests for core.info.info() function with model profile as argument.

    NOTE: These tests are a bit brittle because they rely on hard-coded line numbers in the
    captured stdout.
    """

    @pytest.mark.parametrize(
        "model_profile, expected",
        (
            ("SalishSeaCast-201905", "SalishSeaCast-201905.yaml:"),
            ("SalishSeaCast-201905.yaml", "SalishSeaCast-201905.yaml:"),
        ),
    )
    def test_model_profile_file_name(self, model_profile, expected, capsys):
        info.info(model_profile)

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[0] == expected

    def test_time_bases_and_var_groups(self, capsys):
        info.info("SalishSeaCast-201905")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = [
            "day",
            "auxiliary",
            "biology",
            "biology and chemistry rates",
            "chemistry",
            "grazing and mortality",
            "physics tracers",
            "hour",
            "auxiliary",
            "biology",
            "chemistry",
            "physics tracers",
            "u velocity",
            "v velocity",
            "vertical turbulence",
            "w velocity",
        ]
        assert set(line.strip() for line in stdout_lines[2 : len(expected) + 2]) == set(
            expected
        )


class TestUnrecognizedClusterOrModelProfile:
    """Unit test for core.info.info() is an argument value that is not recognized as either
    a cluster or a model profile.
    """

    def test_bad_cluster_or_model(self, log_output):
        info.info("foo")

        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["cluster_or_model"] == "foo"
        assert log_output.entries[0]["event"] == "unrecognized cluster or model profile"
