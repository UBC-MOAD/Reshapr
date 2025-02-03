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


"""Unit tests for core.info module."""
import os
import textwrap
from importlib import metadata

import numpy
import pandas
import pytest
import xarray
from rich.console import Console

from reshapr.core import info


class TestBasicInfo:
    """Unit tests for core.info.info() function with empty cluster_or_model argument.

    NOTE: These tests are a bit brittle because they rely on hard-coded line numbers in the
    captured stdout.
    """

    @pytest.mark.parametrize(
        "pkg, line",
        (("reshapr", 0), ("xarray", 1), ("dask", 2), ("h5netcdf", 3), ("netcdf4", 4)),
    )
    def test_pkg_version(self, pkg, line, capsys):
        info.info(cluster_or_model="", time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[line] == f"{pkg}, version {metadata.version(pkg)}"

    def test_cluster_configs(self, capsys):
        info.info(cluster_or_model="", time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = {"salish_cluster.yaml"}
        assert set(line.strip() for line in stdout_lines[7:8]) == expected

    def test_model_profiles(self, capsys):
        info.info(cluster_or_model="", time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = {
            "SalishSeaCast-201812.yaml",
            "SalishSeaCast-201905.yaml",
            "SalishSeaCast-201905-month-avg-salish.yaml",
            "SalishSeaCast-202111-salish.yaml",
            "SalishSeaCast-202111-month-avg-salish.yaml",
            "SalishSeaCast-202111-2xrez-salish.yaml",
            "HRDPS-2.5km-GEMLAM-22sep11onward.yaml",
            "HRDPS-2.5km-GEMLAM-pre22sep11.yaml",
            "HRDPS-2.5km-operational.yaml",
        }
        assert (
            set(line.strip() for line in stdout_lines[10 : len(expected) + 10])
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
        info.info(cluster, time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[0] == expected

    def test_cluster_file_contents(self, capsys):
        info.info("salish_cluster.yaml", time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = textwrap.dedent(
            """\
                # Configuration for a dask cluster on salish

                name: salish dask cluster
                processes: True
                number of workers: 4
                threads per worker: 1
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

    def test_user_supplied_profile(self, tmp_path):
        user_provided_profile = tmp_path / "some_profile.yaml"
        user_provided_profile.write_text("")

        is_profile = info._is_model_profile(os.fspath(user_provided_profile))

        assert is_profile


class TestModelProfileInfo:
    """Unit tests for core.info.info() function with model profile as argument.

    NOTE: These tests are a bit brittle because they rely on hard-coded line numbers in the
    captured stdout.
    """

    @pytest.mark.parametrize(
        "model_profile, expected",
        (
            ("SalishSeaCast-202111-salish", "SalishSeaCast-202111-salish.yaml:"),
            ("SalishSeaCast-202111-salish.yaml", "SalishSeaCast-202111-salish.yaml:"),
        ),
    )
    def test_model_profile_file_name(self, model_profile, expected, capsys):
        info.info(model_profile, time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[0] == expected

    def test_missing_description(self, log_output, capsys, tmp_path):
        """This tests for a malformed model profile as well as an attempt to use
        `reshapr info` with a user-provided cluster description.
        """
        cluster_config = tmp_path / "user_cluster.yaml"
        cluster_config.write_text("name: user cluster")

        info.info(os.fspath(cluster_config), "time_interval", "vars_group")

        capsys.readouterr()
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["model_profile"] == {"name": "user cluster"}
        expected = "no description key found in model profile"
        assert log_output.entries[0]["event"] == expected

    def test_model_profile_file_description(self, capsys):
        info.info("SalishSeaCast-202111-salish", time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[1].startswith("  SalishSeaCast version 202111")

    def test_time_bases_and_var_groups(self, capsys):
        info.info("SalishSeaCast-202111-salish", time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        expected = [
            "day",
            "biology",
            "biology growth rates",
            "chemistry",
            "grazing",
            "light",
            "mortality",
            "physics tracers",
            "vvl grid",
            "hour",
            "biology",
            "chemistry",
            "light",
            "physics tracers",
            "turbulence",
            "u velocity",
            "v velocity",
            "vvl grid",
            "w velocity",
        ]
        assert set(line.strip() for line in stdout_lines[5 : len(expected) + 5]) == set(
            expected
        )

    @pytest.mark.parametrize(
        "model_profile",
        (
            "SalishSeaCast-202111-salish",
            "SalishSeaCast-201905-month-avg-salish.yaml",
        ),
    )
    def test_days_per_file_excluded(self, model_profile, capsys):
        info.info(model_profile, time_interval="", vars_group="")

        stdout_lines = capsys.readouterr().out.splitlines()
        stripped_stdout_lines = set(line.strip() for line in stdout_lines)
        assert "days per file" not in stripped_stdout_lines

    @pytest.mark.parametrize(
        "time_interval, vars_group",
        (
            ("hour", ""),
            ("", "biology"),
        ),
    )
    def test_missing_time_interval_or_var_group(
        self, time_interval, vars_group, log_output, capsys
    ):
        info.info("SalishSeaCast-202111-salish", time_interval, vars_group)

        capsys.readouterr()
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["time_interval"] == time_interval
        assert log_output.entries[0]["vars_group"] == vars_group
        expected = "both time interval and variable group are required"
        assert log_output.entries[0]["event"] == expected


class TestUnrecognizedClusterOrModelProfile:
    """Unit test for core.info.info() is an argument value that is not recognized as either
    a cluster or a model profile.
    """

    def test_bad_cluster_or_model(self, log_output):
        info.info("foo", time_interval="", vars_group="")

        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["cluster_or_model"] == "foo"
        assert log_output.entries[0]["event"] == "unrecognized cluster or model profile"


class TestVarsList:
    """Unit tests for core.info._vars_list() function."""

    def test_bad_results_archive_path(self, log_output):
        model_profile = {
            "results archive": {
                "path": "/foo/nowcast-green.201905/",
                "datasets": {
                    "hour": {
                        "biology": {
                            "file pattern": "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
                        }
                    }
                },
            }
        }
        info._vars_list(model_profile, "hour", "biology", Console())

        assert log_output.entries[0]["log_level"] == "error"
        assert (
            log_output.entries[0]["results_archive_path"]
            == "/foo/nowcast-green.201905/"
        )
        assert (
            log_output.entries[0]["event"]
            == "model profile results archive path not found"
        )

    def test_bad_time_interval(self, log_output):
        model_profile = {
            "results archive": {
                "path": "/results2/SalishSea/nowcast-green.201905/",
                "datasets": {
                    "hour": {
                        "biology": {
                            "file pattern": "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
                        }
                    }
                },
            }
        }
        info._vars_list(model_profile, "foo", "biology", Console())

        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["time_interval"] == "foo"
        assert log_output.entries[0]["event"] == "time interval is not in model profile"

    def test_bad_vars_group(self, log_output):
        model_profile = {
            "results archive": {
                "path": "/results2/SalishSea/nowcast-green.201905/",
                "datasets": {
                    "hour": {
                        "biology": {
                            "file pattern": "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
                        }
                    }
                },
            }
        }
        info._vars_list(model_profile, "hour", "foo", Console())

        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["vars_group"] == "foo"
        assert (
            log_output.entries[0]["event"] == "variables group is not in model profile"
        )

    def test_vars_list(self, capsys, tmp_path, monkeypatch):
        model_results_archive = tmp_path / "model_results/"
        model_results_archive.mkdir()
        ds = xarray.Dataset(
            coords={
                "time": pandas.date_range(
                    "2022-07-21",
                    periods=1,
                    freq=pandas.DateOffset(days=1),
                ),
                "depth": numpy.arange(0, 4, 0.5),
                "gridY": numpy.arange(9),
                "gridX": numpy.arange(4),
            },
            data_vars={
                "vosaline": xarray.DataArray(
                    name="vosaline",
                    data=numpy.empty((1, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time": pandas.date_range(
                            "2022-07-21",
                            periods=1,
                            freq=pandas.DateOffset(days=1),
                        ),
                        "depth": numpy.arange(0, 4, 0.5),
                        "gridY": numpy.arange(9),
                        "gridX": numpy.arange(4),
                    },
                    attrs={
                        "long_name": "salinity",
                        "units": "g kg-1",
                    },
                ),
                "votemper": xarray.DataArray(
                    name="votemper",
                    data=numpy.empty((1, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time": pandas.date_range(
                            "2022-07-21",
                            periods=1,
                            freq=pandas.DateOffset(days=1),
                        ),
                        "depth": numpy.arange(0, 4, 0.5),
                        "gridY": numpy.arange(9),
                        "gridX": numpy.arange(4),
                    },
                    attrs={
                        "long_name": "temperature",
                        "units": "degC",
                    },
                ),
            },
            attrs={
                "name": "test_20220721_20220721_grid_T.nc",
                "description": "test dataset for TestVarsList",
            },
        )
        ds.to_netcdf(model_results_archive / "test_20220721_20220721_grid_T.nc")

        model_profile = {
            "name": "TestModel",
            "results archive": {
                "path": os.fspath(model_results_archive),
                "datasets": {
                    "hour": {
                        "physics tracers": {
                            "file pattern": "test_{yyyymmdd}_{yyyymmdd}_grid_T.nc",
                        },
                    },
                },
            },
        }
        info._vars_list(model_profile, "hour", "physics tracers", Console())

        stdout_lines = capsys.readouterr().out.splitlines()
        assert stdout_lines[0] == "hour-averaged variables in physics tracers group:"
        assert stdout_lines[1] == "  - vosaline : salinity [g kg-1]"
        assert stdout_lines[2] == "  - votemper : temperature [degC]"
