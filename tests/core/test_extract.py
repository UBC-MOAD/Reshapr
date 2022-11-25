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


"""Unit tests for core.extract module.
"""
import datetime
import os
import textwrap
from pathlib import Path

import arrow
import numpy
import pandas
import pandas.tseries.offsets
import pytest
import xarray

from reshapr.core import extract


class TestCliExtract:
    """Unit test for core.extract.cli_extract() function."""

    def test_no_config_file(self, log_output, tmp_path):
        nonexistent_config_yaml = tmp_path / "nonexistent.yaml"

        with pytest.raises(SystemExit) as exc_info:
            extract.cli_extract(nonexistent_config_yaml, "", "")

        assert exc_info.value.code == 2
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["config_file"] == os.fspath(
            nonexistent_config_yaml
        )
        assert log_output.entries[0]["event"] == "config file not found"


class TestLoadConfig:
    """Unit tests for core.extract._load_config() function."""

    @pytest.mark.parametrize(
        "start_date_override, end_date_override",
        (
            ("", ""),
            (None, ""),
            ("", None),
            (None, None),
        ),
    )
    def test_load_config_no_date_overrides(
        self, start_date_override, end_date_override, log_output, tmp_path
    ):
        extract_config_yaml = tmp_path / "extract_config.yaml"
        extract_config_yaml.write_text(
            textwrap.dedent(
                """\
                dask cluster: docs/subcommands/salish_cluster.yaml

                start date: 2007-01-01
                end date: 2007-01-10
                """
            )
        )

        config = extract.load_config(
            extract_config_yaml, start_date_override, end_date_override
        )

        assert config["dask cluster"] == "docs/subcommands/salish_cluster.yaml"
        assert config["start date"] == datetime.date(2007, 1, 1)
        assert config["end date"] == datetime.date(2007, 1, 10)

        assert log_output.entries[0]["log_level"] == "info"
        assert log_output.entries[0]["config_file"] == os.fspath(extract_config_yaml)
        assert log_output.entries[0]["event"] == "loaded config"

    def test_no_config_file(self, log_output, tmp_path):
        nonexistent_config_yaml = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            extract.load_config(nonexistent_config_yaml, None, None)

    @pytest.mark.parametrize(
        "start_date_override, end_date_override, expected_start_date, expected_end_date",
        (
            ("2022-11-01", "", datetime.date(2022, 11, 1), datetime.date(2007, 1, 10)),
            (
                "2022-11-01",
                None,
                datetime.date(2022, 11, 1),
                datetime.date(2007, 1, 10),
            ),
            ("", "2022-11-02", datetime.date(2007, 1, 1), datetime.date(2022, 11, 2)),
            (None, "2022-11-02", datetime.date(2007, 1, 1), datetime.date(2022, 11, 2)),
            (
                "2022-11-01",
                "2022-11-02",
                datetime.date(2022, 11, 1),
                datetime.date(2022, 11, 2),
            ),
            (
                arrow.get("2022-11-01"),
                arrow.get("2022-11-02"),
                datetime.date(2022, 11, 1),
                datetime.date(2022, 11, 2),
            ),
            (
                datetime.date(2022, 11, 1),
                datetime.date(2022, 11, 2),
                datetime.date(2022, 11, 1),
                datetime.date(2022, 11, 2),
            ),
        ),
    )
    def test_load_config_date_overrides(
        self,
        start_date_override,
        end_date_override,
        expected_start_date,
        expected_end_date,
        log_output,
        tmp_path,
    ):
        extract_config_yaml = tmp_path / "extract_config.yaml"
        extract_config_yaml.write_text(
            textwrap.dedent(
                """\
                dask cluster: docs/subcommands/salish_cluster.yaml

                start date: 2007-01-01
                end date: 2007-01-10
                """
            )
        )

        config = extract.load_config(
            extract_config_yaml, start_date_override, end_date_override
        )

        assert config["start date"] == expected_start_date
        assert config["end date"] == expected_end_date


class TestNormalizeEndDate:
    """Unit tests for _normalize_end_date() function."""

    @pytest.mark.parametrize(
        "cli_end_date, expected",
        (
            ("", ""),
            ("2022-01-31", "2022-01-31"),
            ("2022-02-31", "2022-02-28"),
            ("2020-02-31", "2020-02-29"),
            ("2022-06-31", "2022-06-30"),
        ),
    )
    def test_normalize_end_date(self, cli_end_date, expected):
        normalized_end_date = extract._normalize_end_date(cli_end_date)

        assert normalized_end_date == expected


class TestOverrideStartEndDate:
    """Unit tests for _override_start_end_date() function."""

    def test_no_override(self):
        config = {
            "start date": datetime.date(2007, 1, 1),
            "end date": datetime.date(2007, 12, 31),
        }
        cli_start_date, cli_end_date = "", ""

        start_date, end_date = extract._override_start_end_date(
            config, cli_start_date, cli_end_date
        )

        assert start_date == datetime.date(2007, 1, 1)
        assert end_date == datetime.date(2007, 12, 31)

    def test_override(self):
        config = {
            "start date": datetime.date(2007, 1, 1),
            "end date": datetime.date(2007, 12, 31),
        }
        cli_start_date, cli_end_date = "2022-06-15", "2022-06-16"

        start_date, end_date = extract._override_start_end_date(
            config, cli_start_date, cli_end_date
        )

        assert start_date == datetime.date(2022, 6, 15)
        assert end_date == datetime.date(2022, 6, 16)


class TestReconstructCmdLine:
    """Unit tests for _reconstruct_cmd_line() function."""

    def test_no_start_end_date_override(self):
        config_yaml = Path("test_extract.yaml")
        cli_start_date, cli_end_date = "", ""

        cmd_line = extract._reconstruct_cmd_line(
            config_yaml, cli_start_date, cli_end_date
        )

        assert cmd_line == f"`reshapr extract {config_yaml.absolute()}`"

    def test_with_start_end_date_override(self):
        config_yaml = Path("test_extract.yaml")
        cli_start_date, cli_end_date = "2022-06-02", "2022-06-15"

        cmd_line = extract._reconstruct_cmd_line(
            config_yaml, cli_start_date, cli_end_date
        )

        expected = (
            f"`reshapr extract {config_yaml.absolute()}"
            f" --start-date 2022-06-02 --end-date 2022-06-15`"
        )
        assert cmd_line == expected

    def test_with_start_date_override(self):
        config_yaml = Path("test_extract.yaml")
        cli_start_date, cli_end_date = "2022-06-02", ""

        cmd_line = extract._reconstruct_cmd_line(
            config_yaml, cli_start_date, cli_end_date
        )

        assert (
            cmd_line
            == f"`reshapr extract {config_yaml.absolute()} --start-date 2022-06-02`"
        )

    def test_with_end_date_override(self):
        config_yaml = Path("test_extract.yaml")
        cli_start_date, cli_end_date = "", "2022-06-15"

        cmd_line = extract._reconstruct_cmd_line(
            config_yaml, cli_start_date, cli_end_date
        )

        assert (
            cmd_line
            == f"`reshapr extract {config_yaml.absolute()} --end-date 2022-06-15`"
        )


class TestLoadModelProfile:
    """Unit tests for core.extract._load_model_profile() function."""

    def test_load_model_profile_from_path(self, log_output, tmp_path):
        model_results_archive = tmp_path / "model_results/"
        model_results_archive.mkdir()
        model_profile_yaml = tmp_path / "model_profile.yaml"
        model_profile_yaml.write_text(
            textwrap.dedent(
                f"""\
                name: SomeModel

                results archive:
                  path: {os.fspath(model_results_archive)}
                """
            )
        )

        model_profile = extract._load_model_profile(model_profile_yaml)

        assert model_profile["name"] == "SomeModel"

        assert log_output.entries[0]["log_level"] == "info"
        assert log_output.entries[0]["model_profile_yaml"] == os.fspath(
            model_profile_yaml
        )
        assert log_output.entries[0]["event"] == "loaded model profile"

    def test_load_model_profile_from_model_profiles_dir(self, log_output, monkeypatch):
        def mock_exists(path):
            return True

        monkeypatch.setattr(Path, "exists", mock_exists)

        model_profile_yaml = Path("SalishSeaCast-201812.yaml")

        model_profile = extract._load_model_profile(model_profile_yaml)

        assert model_profile["description"].startswith(
            "SalishSeaCast version 201812 NEMO results"
        )

        assert log_output.entries[0]["log_level"] == "info"
        model_profiles_path = Path(__file__).parent.parent.parent / "model_profiles"
        assert log_output.entries[0]["model_profile_yaml"] == os.fspath(
            model_profiles_path / model_profile_yaml
        )
        assert log_output.entries[0]["event"] == "loaded model profile"

    def test_no_model_profile_file_from_path(self, log_output, tmp_path):
        nonexistent_model_profile_yaml = tmp_path / "nonexistent.yaml"

        with pytest.raises(SystemExit) as exc_info:
            extract._load_model_profile(nonexistent_model_profile_yaml)

        assert exc_info.value.code == 2
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["model_profile_yaml"] == os.fspath(
            nonexistent_model_profile_yaml
        )
        assert log_output.entries[0]["event"] == "model profile file not found"

    def test_no_model_profile_in_model_profiles_dir(self, log_output):
        nonexistent_model_profile_yaml = Path("nonexistent.yaml")

        with pytest.raises(SystemExit) as exc_info:
            extract._load_model_profile(nonexistent_model_profile_yaml)

        assert exc_info.value.code == 2
        assert log_output.entries[0]["log_level"] == "error"
        model_profiles_path = Path(__file__).parent.parent.parent / "model_profiles"
        assert log_output.entries[0]["model_profile_yaml"] == os.fspath(
            model_profiles_path / nonexistent_model_profile_yaml
        )
        assert log_output.entries[0]["event"] == "model profile file not found"

    def test_no_results_archive(self, log_output, tmp_path):
        nonexistent_path = Path("/this/path/does/not/exist/")
        model_profile_yaml = tmp_path / "model_profile.yaml"
        model_profile_yaml.write_text(
            textwrap.dedent(
                f"""\
                name: SomeModel

                results archive:
                  path: {os.fspath(nonexistent_path)}
                """
            )
        )

        with pytest.raises(SystemExit) as exc_info:
            extract._load_model_profile(model_profile_yaml)

        assert exc_info.value.code == 2
        assert log_output.entries[1]["log_level"] == "error"
        assert log_output.entries[1]["model_profile_yaml"] == os.fspath(
            model_profile_yaml
        )
        assert log_output.entries[1]["results_archive"] == os.fspath(nonexistent_path)
        assert log_output.entries[1]["event"] == "model results archive not found"


class TestCalcDsPaths:
    """Unit tests for calc_ds_paths() function."""

    def test_SalishSeaCast_ds_paths(self, log_output):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "start date": datetime.date(2015, 1, 1),
            "end date": datetime.date(2015, 1, 2),
        }
        model_profile = {
            "results archive": {
                "path": "/results/SalishSea/nowcast-green.201812/",
                "datasets": {
                    "day": {
                        "biology": {
                            "file pattern": "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
                        },
                    },
                },
            },
        }

        ds_paths = extract.calc_ds_paths(extract_config, model_profile)

        expected_paths = [
            Path(
                "/results/SalishSea/nowcast-green.201812/01jan15/SalishSea_1d_20150101_20150101_ptrc_T.nc"
            ),
            Path(
                "/results/SalishSea/nowcast-green.201812/02jan15/SalishSea_1d_20150102_20150102_ptrc_T.nc"
            ),
        ]
        assert ds_paths == expected_paths

        assert log_output.entries[0]["log_level"] == "debug"
        expected = os.fspath(Path(model_profile["results archive"]["path"]))
        assert log_output.entries[0]["results_archive_path"] == expected
        assert log_output.entries[0]["time_base"] == "day"
        assert log_output.entries[0]["vars_group"] == "biology"
        assert (
            log_output.entries[0]["nc_files_pattern"]
            == "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
        )
        assert log_output.entries[0]["start_date"] == "2015-01-01"
        assert log_output.entries[0]["end_date"] == "2015-01-02"
        assert log_output.entries[0]["n_datasets"] == 2
        assert log_output.entries[0]["event"] == "collected dataset paths"

    def test_HRDPS_ds_paths(self, log_output):
        extract_config = {
            "dataset": {
                "time base": "hour",
                "variables group": "surface fields",
            },
            "start date": datetime.date(2015, 1, 1),
            "end date": datetime.date(2015, 1, 2),
        }
        model_profile = {
            "results archive": {
                "path": "/results/forcing/atmospheric/GEM2.5/operational/",
                "datasets": {
                    "hour": {
                        "surface fields": {"file pattern": "ops_{nemo_yyyymmdd}.nc"},
                    },
                },
            },
        }

        ds_paths = extract.calc_ds_paths(extract_config, model_profile)

        expected_paths = [
            Path("/results/forcing/atmospheric/GEM2.5/operational/ops_y2015m01d01.nc"),
            Path("/results/forcing/atmospheric/GEM2.5/operational/ops_y2015m01d02.nc"),
        ]
        assert ds_paths == expected_paths

        assert log_output.entries[0]["log_level"] == "debug"
        expected = os.fspath(Path(model_profile["results archive"]["path"]))
        assert log_output.entries[0]["results_archive_path"] == expected
        assert log_output.entries[0]["time_base"] == "hour"
        assert log_output.entries[0]["vars_group"] == "surface fields"
        assert log_output.entries[0]["nc_files_pattern"] == "ops_{nemo_yyyymmdd}.nc"
        assert log_output.entries[0]["start_date"] == "2015-01-01"
        assert log_output.entries[0]["end_date"] == "2015-01-02"
        assert log_output.entries[0]["n_datasets"] == 2
        assert log_output.entries[0]["event"] == "collected dataset paths"


class TestCalcDsChunks:
    """Unit tests for calc_ds_chunk() function."""

    def test_calc_ds_chunks(self, log_output):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "start date": datetime.date(2015, 1, 1),
            "end date": datetime.date(2015, 1, 2),
        }
        model_profile = {
            "time coord": {
                "name": "time_counter",
            },
            "chunk size": {
                "time": 1,
                "depth": 40,
                "y": 898,
                "x": 398,
            },
            "results archive": {
                "datasets": {
                    "day": {
                        "biology": {"depth coord": "deptht"},
                    },
                },
            },
        }

        chunk_size = extract.calc_ds_chunk_size(extract_config, model_profile)

        expected = {
            "time_counter": 1,
            "deptht": 40,
            "y": 898,
            "x": 398,
        }
        assert chunk_size == expected

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["chunk_size"] == expected
        assert log_output.entries[0]["event"] == "chunk size for dataset loading"

    def test_calc_ds_chunks_no_depth(self, log_output):
        extract_config = {
            "dataset": {
                "time base": "hour",
                "variables group": "surface fields",
            },
            "start date": datetime.date(2015, 1, 1),
            "end date": datetime.date(2015, 1, 2),
        }
        model_profile = {
            "time coord": {
                "name": "time_counter",
            },
            "chunk size": {
                "time": 24,
                "y": 266,
                "x": 256,
            },
        }

        chunk_size = extract.calc_ds_chunk_size(extract_config, model_profile)

        expected = {
            "time_counter": 24,
            "y": 266,
            "x": 256,
        }
        assert chunk_size == expected

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["chunk_size"] == expected
        assert log_output.entries[0]["event"] == "chunk size for dataset loading"

    def test_model_profile_chunk_size_unchanged(self, log_output):
        """Test to demonstrate bug whereby model profile chunk size dict was getting changed
        in the course of calculating the dataset loading chunk size dict.
        """
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "start date": datetime.date(2015, 1, 1),
            "end date": datetime.date(2015, 1, 2),
        }
        model_profile = {
            "time coord": {
                "name": "time_counter",
            },
            "chunk size": {
                "time": 1,
                "depth": 40,
                "y": 898,
                "x": 398,
            },
            "results archive": {
                "datasets": {
                    "day": {
                        "biology": {"depth coord": "deptht"},
                    },
                },
            },
        }

        extract.calc_ds_chunk_size(extract_config, model_profile)

        expected = {
            "time": 1,
            "depth": 40,
            "y": 898,
            "x": 398,
        }
        assert model_profile["chunk size"] == expected


class TestCreateDataarray:
    """Unit tests for create_dataarray() function."""

    def test_create_coord_array(self):
        source_array = xarray.DataArray(
            name="test source array",
            data=numpy.arange(43),
        )
        attrs = {"foo": "bar"}

        coord = extract.create_dataarray("test", source_array, attrs)

        assert coord.name == "test"
        assert numpy.array_equal(coord.data, source_array.data)
        assert numpy.array_equal(coord.coords["test"], source_array.data)
        assert coord.attrs == attrs

    def test_create_var_array(self):
        source_array = xarray.DataArray(
            name="test source array",
            data=numpy.arange(43),
        )
        attrs = {"bar": "foo"}
        coords = {"time": numpy.arange(43, 0, -1)}

        var = extract.create_dataarray("test", source_array, attrs, coords)

        assert var.name == "test"
        assert numpy.array_equal(var.data, source_array.data)
        assert numpy.array_equal(var.coords["time"], coords["time"])
        assert var.attrs == attrs


class TestOpenDataset:
    """Unit test for open_dataset() function."""

    @pytest.fixture(name="source_dataset", scope="class")
    def fixture_source_dataset(self):
        return xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "deptht": numpy.arange(0, 4, 0.5),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.ones((4, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "deptht": numpy.arange(0, 4, 0.5),
                        "y": numpy.arange(9),
                        "x": numpy.arange(4),
                    },
                    attrs={
                        "standard_name": "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water",
                        "long_name": "Diatoms Concentration",
                        "units": "mmol m-3",
                    },
                ),
            },
        )

    def test_open_dataset(self, source_dataset, log_output, tmp_path):
        results_archive = tmp_path / "results_archive"
        results_archive.mkdir()
        source_dataset.to_netcdf(results_archive / "test_dataset.nc")
        ds_paths = [results_archive / "test_dataset.nc"]
        chunk_size = {
            "time_counter": 4,
            "deptht": 8,
            "y": 9,
            "x": 4,
        }
        extract_config = {
            "extract variables": [
                "diatoms",
            ]
        }
        ds = extract.open_dataset(ds_paths, chunk_size, extract_config)

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "opened dataset"
        assert log_output.entries[0]["ds"] == ds

        xarray.testing.assert_equal(ds, source_dataset)

    def test_exit_when_no_dataset_vars(self, source_dataset, log_output, tmp_path):
        """re: issue #37

        Confirm that processing ends with SystemExit(2) and appropriate error message in log
        when that conditions that give rise to issue #37
        (KeyError for variable not in variables group) occur.
        """
        results_archive = tmp_path / "results_archive"
        results_archive.mkdir()
        source_dataset.to_netcdf(results_archive / "test_dataset.nc")
        ds_paths = [results_archive / "test_dataset.nc"]
        chunk_size = {
            "time_counter": 4,
            "deptht": 8,
            "y": 9,
            "x": 4,
        }
        extract_config = {
            "extract variables": [
                "nitrate",
            ]
        }

        with pytest.raises(SystemExit) as exc_info:
            extract.open_dataset(ds_paths, chunk_size, extract_config)

        assert exc_info.value.code == 2
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["event"] == "no variables in source dataset"
        assert log_output.entries[0]["extract_vars"] == {"nitrate"}
        expected = "typo in variable name, or incorrect variables group"
        assert log_output.entries[0]["possible_reasons"] == expected


class TestCalcOutputCoords:
    """Unit tests for calc_output_coords() function."""

    @pytest.fixture(name="model_profile", scope="class")
    def fixture_model_profile(self):
        return {
            "time coord": {
                "name": "time_counter",
            },
            "y coord": {
                "name": "y",
            },
            "x coord": {
                "name": "x",
            },
            "chunk size": {
                "time": 1,
                "depth": 9,
                "y": 9,
                "x": 4,
            },
            "extraction time origin": "2015-01-01",
            "results archive": {
                "datasets": {
                    "day": {
                        "biology": {"depth coord": "deptht"},
                    },
                    "hour": {
                        "biology": {"depth coord": "deptht"},
                    },
                }
            },
        }

    @pytest.fixture(name="source_dataset", scope="class")
    def fixture_source_dataset(self):
        return xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "deptht": numpy.arange(0, 4, 0.5),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.ones((4, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "deptht": numpy.arange(0, 4, 0.5),
                        "y": numpy.arange(9),
                        "x": numpy.arange(4),
                    },
                    attrs={
                        "standard_name": "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water",
                        "long_name": "Diatoms Concentration",
                        "units": "mmol m-3",
                    },
                ),
            },
        )

    @pytest.mark.parametrize(
        "use_model_coords, coord_name, time_base, example",
        (
            (
                True,
                "time_counter",
                "day",
                "8 February 2022 have a time value of 2022-02-08 12:00:00Z",
            ),
            (
                False,
                "time",
                "day",
                "8 February 2022 have a time value of 2022-02-08 12:00:00Z",
            ),
            (
                True,
                "time_counter",
                "hour",
                "the first hour of 8 February 2022 have a time value of 2022-02-08 00:30:00Z",
            ),
            (
                False,
                "time",
                "hour",
                "the first hour of 8 February 2022 have a time value of 2022-02-08 00:30:00Z",
            ),
        ),
    )
    def test_time_coord(
        self,
        use_model_coords,
        coord_name,
        time_base,
        example,
        source_dataset,
        model_profile,
        log_output,
    ):
        extract_config = {
            "dataset": {
                "time base": time_base,
                "variables group": "biology",
            },
            "extracted dataset": {
                "use model coords": use_model_coords,
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords[coord_name].name == coord_name
        assert numpy.array_equal(
            output_coords[coord_name].data, source_dataset.time_counter.data
        )
        assert output_coords[coord_name].attrs["standard_name"] == "time"
        assert output_coords[coord_name].attrs["long_name"] == "Time Axis"
        expected = (
            f"time values are UTC at the centre of the intervals over which the "
            f"calculated model results are averaged; e.g. the field average values for "
            f"{example}"
        )
        assert output_coords[coord_name].attrs["comment"] == expected

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extraction time coordinate"

    @pytest.mark.parametrize(
        "time_base, time_offset, example",
        (
            (
                "day",
                "12:00:00",
                "8 February 2022 have a time value of 2022-02-08 12:00:00Z",
            ),
            (
                "hour",
                "00:30:00",
                "the first hour of 8 February 2022 have a time value of 2022-02-08 00:30:00Z",
            ),
        ),
    )
    def test_time_coord_selection(
        self, time_base, time_offset, example, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": time_base,
                "variables group": "biology",
            },
            "selection": {
                "time interval": 3,
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["time"].name == "time"
        assert numpy.array_equal(
            output_coords["time"].data,
            source_dataset.time_counter.isel(time_counter=slice(0, None, 3)),
        )
        assert output_coords["time"].attrs["standard_name"] == "time"
        assert output_coords["time"].attrs["long_name"] == "Time Axis"
        assert output_coords["time"].attrs["time_origin"] == f"2015-01-01 {time_offset}"
        expected = (
            f"time values are UTC at the centre of the intervals over which the "
            f"calculated model results are averaged; e.g. the field average values for "
            f"{example}"
        )
        assert output_coords["time"].attrs["comment"] == expected

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extraction time coordinate"

    @pytest.mark.parametrize(
        "use_model_coords, time_coord_name, y_coord_name, x_coord_name",
        (
            (True, "time_counter", "y", "x"),
            (False, "time", "gridY", "gridX"),
        ),
    )
    def test_no_depth_coord(
        self, use_model_coords, time_coord_name, y_coord_name, x_coord_name
    ):
        model_profile = {
            "time coord": {
                "name": "time_counter",
            },
            "y coord": {
                "name": "y",
            },
            "x coord": {
                "name": "x",
            },
            "chunk size": {
                "time": 4,
                "y": 9,
                "x": 4,
            },
            "extraction time origin": "2007-01-01",
            "results archive": {
                "datasets": {
                    "hour": {
                        "surface fields": {},
                    },
                }
            },
        }
        source_dataset = xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "atmpres": xarray.DataArray(
                    name="atmpres",
                    data=numpy.ones((4, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "y": numpy.arange(9),
                        "x": numpy.arange(4),
                    },
                    attrs={
                        "standard_name": "PRMSL_meansealevel",
                        "long_name": "Pressure Reduced to MSL",
                        "units": "Pa",
                    },
                ),
            },
        )
        extract_config = {
            "dataset": {
                "time base": "hour",
                "variables group": "surface fields",
            },
            "extracted dataset": {
                "use model coords": use_model_coords,
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert "depth" not in output_coords

        assert output_coords[time_coord_name].name == time_coord_name
        assert output_coords[y_coord_name].name == y_coord_name
        assert output_coords[x_coord_name].name == x_coord_name

    def test_var_without_depth_coord(self, model_profile):
        source_dataset = xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "deptht": numpy.arange(0, 4, 0.5),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "sossheig": xarray.DataArray(
                    name="sossheig",
                    data=numpy.ones((4, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "y": numpy.arange(9),
                        "x": numpy.arange(4),
                    },
                    attrs={
                        "standard_name": "sea_surface_height_above_geoid",
                        "long_name": "Sea Surface Height",
                        "units": "m",
                    },
                ),
            },
        )
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert "depth" not in output_coords

    @pytest.mark.parametrize(
        "use_model_coords, coord_name",
        (
            (True, "deptht"),
            (False, "depth"),
        ),
    )
    def test_depth_coord(
        self, use_model_coords, coord_name, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "extracted dataset": {
                "use model coords": use_model_coords,
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords[coord_name].name == coord_name
        assert numpy.array_equal(
            output_coords[coord_name].data, source_dataset.deptht.data
        )
        assert output_coords[coord_name].attrs["standard_name"] == "sea_floor_depth"
        assert output_coords[coord_name].attrs["long_name"] == "Sea Floor Depth"
        assert output_coords[coord_name].attrs["units"] == "metres"
        assert output_coords[coord_name].attrs["positive"] == "down"

        assert log_output.entries[1]["log_level"] == "debug"
        assert log_output.entries[1]["event"] == "extraction depth coordinate"

    def test_depth_coord_depth_selection_min(self, source_dataset, model_profile):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "depth": {
                    "depth min": 5,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["depth"].name == "depth"
        assert numpy.array_equal(
            output_coords["depth"].data,
            # stop=None in slice() means the length of the array without having to know what that is
            source_dataset.deptht.isel(deptht=slice(5, None)),
        )

    def test_depth_coord_depth_selection_max(self, source_dataset, model_profile):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "depth": {
                    "depth max": 5,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["depth"].name == "depth"
        assert numpy.array_equal(
            output_coords["depth"].data, source_dataset.deptht.isel(deptht=slice(0, 5))
        )

    def test_depth_coord_depth_selection_interval(self, source_dataset, model_profile):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "depth": {
                    "depth interval": 2,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["depth"].name == "depth"
        assert numpy.array_equal(
            output_coords["depth"].data,
            # stop=None in slice() means the length of the array without having to know what that is
            source_dataset.deptht.isel(deptht=slice(0, None, 2)),
        )

    @pytest.mark.parametrize(
        "use_model_coords, coord_name",
        (
            (True, "y"),
            (False, "gridY"),
        ),
    )
    def test_y_index_coord(
        self, use_model_coords, coord_name, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "extracted dataset": {
                "use model coords": use_model_coords,
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords[coord_name].name == coord_name
        assert numpy.array_equal(output_coords[coord_name].data, source_dataset.y.data)
        assert output_coords[coord_name].attrs["standard_name"] == "y"
        assert output_coords[coord_name].attrs["long_name"] == "Grid Y"
        assert output_coords[coord_name].attrs["units"] == "count"
        assert (
            output_coords[coord_name].attrs["comment"]
            == f"{coord_name} values are grid indices in the model y-direction"
        )

        assert log_output.entries[2]["log_level"] == "debug"
        assert log_output.entries[2]["event"] == "extraction y coordinate"

    def test_y_index_coord_cast_to_int(self, log_output):
        source_dataset = xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "y": numpy.arange(9, dtype=float),
                "x": numpy.arange(4, dtype=float),
            },
            data_vars={
                "atmpres": xarray.DataArray(
                    name="atmpres",
                    data=numpy.ones((4, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "y": numpy.arange(9, dtype=float),
                        "x": numpy.arange(4, dtype=float),
                    },
                    attrs={
                        "short_name": "PRMSL_meansealevel",
                        "long_name": "Pressure Reduced to MSL",
                        "units": "Pa",
                    },
                ),
            },
        )
        model_profile = {
            "time coord": {
                "name": "time_counter",
            },
            "y coord": {
                "name": "y",
                "units": "metres",
                "comment": "gridY values are distance in metres in the model y-direction from the south-west corner of the grid",
            },
            "x coord": {
                "name": "x",
                "units": "metres",
                "comment": "gridX values are distance in metres in the model x-direction from the south-west corner of the grid",
            },
            "chunk size": {
                "time": 4,
                "y": 5,
                "x": 4,
            },
            "extraction time origin": "2007-01-01",
            "results archive": {
                "datasets": {
                    "hour": {
                        "surface fields": {},
                    }
                }
            },
        }
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(output_coords["gridY"].data, source_dataset.y.data)
        assert output_coords["gridY"].dtype == numpy.dtype(int)
        assert output_coords["gridY"].attrs["standard_name"] == "y"
        assert output_coords["gridY"].attrs["long_name"] == "Grid Y"
        assert output_coords["gridY"].attrs["units"] == "metres"
        assert (
            output_coords["gridY"].attrs["comment"]
            == "gridY values are distance in metres in the model y-direction from the south-west corner of the grid"
        )

        assert log_output.entries[1]["log_level"] == "debug"
        assert log_output.entries[1]["event"] == "extraction y coordinate"

    def test_y_index_coord_selection_y_min(
        self, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "grid y": {
                    "y min": 6,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(
            output_coords["gridY"].data, source_dataset.y.isel(y=slice(6, None))
        )
        assert output_coords["gridY"].attrs["standard_name"] == "y"
        assert output_coords["gridY"].attrs["long_name"] == "Grid Y"
        assert output_coords["gridY"].attrs["units"] == "count"
        assert (
            output_coords["gridY"].attrs["comment"]
            == "gridY values are grid indices in the model y-direction"
        )

        assert log_output.entries[2]["log_level"] == "debug"
        assert log_output.entries[2]["event"] == "extraction y coordinate"

    def test_y_index_coord_selection_y_max(
        self, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "grid y": {
                    "y max": 3,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(
            output_coords["gridY"].data, source_dataset.y.isel(y=slice(0, 3))
        )
        assert output_coords["gridY"].attrs["standard_name"] == "y"
        assert output_coords["gridY"].attrs["long_name"] == "Grid Y"
        assert output_coords["gridY"].attrs["units"] == "count"
        assert (
            output_coords["gridY"].attrs["comment"]
            == "gridY values are grid indices in the model y-direction"
        )

        assert log_output.entries[2]["log_level"] == "debug"
        assert log_output.entries[2]["event"] == "extraction y coordinate"

    def test_y_index_coord_selection_y_interval(
        self, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "grid y": {
                    "y interval": 2,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(
            output_coords["gridY"].data, source_dataset.y.isel(y=slice(0, None, 2))
        )
        assert output_coords["gridY"].attrs["standard_name"] == "y"
        assert output_coords["gridY"].attrs["long_name"] == "Grid Y"
        assert output_coords["gridY"].attrs["units"] == "count"
        assert (
            output_coords["gridY"].attrs["comment"]
            == "gridY values are grid indices in the model y-direction"
        )

        assert log_output.entries[2]["log_level"] == "debug"
        assert log_output.entries[2]["event"] == "extraction y coordinate"

    @pytest.mark.parametrize(
        "use_model_coords, coord_name",
        (
            (True, "x"),
            (False, "gridX"),
        ),
    )
    def test_x_index_coord(
        self, use_model_coords, coord_name, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "extracted dataset": {
                "use model coords": use_model_coords,
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords[coord_name].name == coord_name
        assert numpy.array_equal(output_coords[coord_name].data, source_dataset.x.data)
        assert output_coords[coord_name].attrs["standard_name"] == "x"
        assert output_coords[coord_name].attrs["long_name"] == "Grid X"
        assert output_coords[coord_name].attrs["units"] == "count"
        assert (
            output_coords[coord_name].attrs["comment"]
            == f"{coord_name} values are grid indices in the model x-direction"
        )

        assert log_output.entries[3]["log_level"] == "debug"
        assert log_output.entries[3]["event"] == "extraction x coordinate"

    def test_x_index_coord_cast_to_int(self, log_output):
        source_dataset = xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "y": numpy.arange(9, dtype=float),
                "x": numpy.arange(4, dtype=float),
            },
            data_vars={
                "atmpres": xarray.DataArray(
                    name="atmpres",
                    data=numpy.ones((4, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "y": numpy.arange(9, dtype=float),
                        "x": numpy.arange(4, dtype=float),
                    },
                    attrs={
                        "short_name": "PRMSL_meansealevel",
                        "long_name": "Pressure Reduced to MSL",
                        "units": "Pa",
                    },
                ),
            },
        )
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "extracted dataset": {},
        }
        model_profile = {
            "time coord": {
                "name": "time_counter",
            },
            "y coord": {
                "name": "y",
                "units": "metres",
                "comment": "gridY values are distance in metres in the model y-direction from the south-west corner of the grid",
            },
            "x coord": {
                "name": "x",
                "units": "metres",
                "comment": "gridX values are distance in metres in the model x-direction from the south-west corner of the grid",
            },
            "chunk size": {
                "time": 4,
                "y": 5,
                "x": 4,
            },
            "extraction time origin": "2007-01-01",
            "results archive": {
                "datasets": {
                    "hour": {
                        "surface fields": {},
                    }
                }
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        assert numpy.array_equal(output_coords["gridX"].data, source_dataset.x.data)
        assert output_coords["gridX"].dtype == numpy.dtype(int)
        assert output_coords["gridX"].attrs["standard_name"] == "x"
        assert output_coords["gridX"].attrs["long_name"] == "Grid X"
        assert output_coords["gridX"].attrs["units"] == "metres"
        assert (
            output_coords["gridX"].attrs["comment"]
            == "gridX values are distance in metres in the model x-direction from the south-west corner of the grid"
        )

        assert log_output.entries[2]["log_level"] == "debug"
        assert log_output.entries[2]["event"] == "extraction x coordinate"

    def test_x_index_coord_selection_x_min(
        self, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "grid x": {
                    "x min": 1,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        # stop=None in slice() means the length of the array without having to know what that is
        assert numpy.array_equal(
            output_coords["gridX"].data, source_dataset.x.isel(x=slice(1, None))
        )
        assert output_coords["gridX"].attrs["standard_name"] == "x"
        assert output_coords["gridX"].attrs["long_name"] == "Grid X"
        assert output_coords["gridX"].attrs["units"] == "count"
        assert (
            output_coords["gridX"].attrs["comment"]
            == "gridX values are grid indices in the model x-direction"
        )

        assert log_output.entries[3]["log_level"] == "debug"
        assert log_output.entries[3]["event"] == "extraction x coordinate"

    def test_x_index_coord_selection_x_max(
        self, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "grid x": {
                    "x max": 3,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        assert numpy.array_equal(
            output_coords["gridX"].data, source_dataset.x.isel(x=slice(0, 3))
        )
        assert output_coords["gridX"].attrs["standard_name"] == "x"
        assert output_coords["gridX"].attrs["long_name"] == "Grid X"
        assert output_coords["gridX"].attrs["units"] == "count"
        assert (
            output_coords["gridX"].attrs["comment"]
            == "gridX values are grid indices in the model x-direction"
        )

        assert log_output.entries[3]["log_level"] == "debug"
        assert log_output.entries[3]["event"] == "extraction x coordinate"

    def test_x_index_coord_selection_x_interval(
        self, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "grid x": {
                    "x interval": 2,
                },
            },
            "extracted dataset": {},
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        # stop=None in slice() means the length of the array without having to know what that is
        assert numpy.array_equal(
            output_coords["gridX"].data, source_dataset.x.isel(x=slice(0, None, 2))
        )
        assert output_coords["gridX"].attrs["standard_name"] == "x"
        assert output_coords["gridX"].attrs["long_name"] == "Grid X"
        assert output_coords["gridX"].attrs["units"] == "count"
        assert (
            output_coords["gridX"].attrs["comment"]
            == "gridX values are grid indices in the model x-direction"
        )

        assert log_output.entries[3]["log_level"] == "debug"
        assert log_output.entries[3]["event"] == "extraction x coordinate"


class TestCalcExtractedVars:
    """Unit tests for calc_extracted_vars() function."""

    @pytest.fixture(name="source_dataset", scope="class")
    def fixture_source_dataset(self):
        return xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "deptht": numpy.arange(0, 4, 0.5),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.ones((4, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "deptht": numpy.arange(0, 4, 0.5),
                        "y": numpy.arange(9),
                        "x": numpy.arange(4),
                    },
                    attrs={
                        "standard_name": "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water",
                        "long_name": "Diatoms Concentration",
                        "units": "mmol m-3",
                    },
                ),
            },
        )

    @pytest.fixture(name="model_profile", scope="class")
    def fixture_model_profile(self):
        return {
            "time coord": {
                "name": "time_counter",
            },
            "y coord": {
                "name": "y",
            },
            "x coord": {
                "name": "x",
            },
            "chunk size": {
                "time": 4,
                "depth": 8,
                "y": 9,
                "x": 4,
            },
            "results archive": {
                "datasets": {
                    "hour": {
                        "biology": {
                            "depth coord": "deptht",
                        }
                    }
                }
            },
        }

    def test_extract_var(self, source_dataset, model_profile, log_output):
        output_coords = {
            "time": numpy.arange(4),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {
            "dataset": {
                "time base": "hour",
                "variables group": "biology",
            },
        }

        extracted_vars = extract.calc_extracted_vars(
            source_dataset, output_coords, config, model_profile
        )

        assert extracted_vars[0].name == "diatoms"
        assert numpy.array_equal(
            extracted_vars[0].data, numpy.ones((4, 8, 9, 4), dtype=numpy.single)
        )
        assert (
            extracted_vars[0].attrs["standard_name"]
            == "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water"
        )
        assert extracted_vars[0].attrs["long_name"] == "Diatoms Concentration"
        assert extracted_vars[0].attrs["units"] == "mmol m-3"
        for coord in output_coords:
            assert numpy.array_equal(
                extracted_vars[0].coords[coord], output_coords[coord]
            )

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted diatoms"

    def test_extract_var_no_depth_coord(self, log_output):
        source_dataset = xarray.Dataset(
            coords={
                "time_counter": numpy.arange(24),
                "y": numpy.arange(5),
                "x": numpy.arange(4),
            },
            data_vars={
                "atmpres": xarray.DataArray(
                    name="atmpres",
                    data=numpy.ones((24, 5, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(24),
                        "y": numpy.arange(5),
                        "x": numpy.arange(4),
                    },
                    attrs={
                        "short_name": "PRMSL_meansealevel",
                        "long_name": "Pressure Reduced to MSL",
                        "units": "Pa",
                    },
                ),
            },
        )
        output_coords = {
            "time": numpy.arange(24),
            "gridY": numpy.arange(5),
            "gridX": numpy.arange(4),
        }
        config = {
            "dataset": {
                "time base": "hour",
                "variables group": "surface fields",
            },
        }
        model_profile = {
            "time coord": {
                "name": "time_counter",
            },
            "y coord": {
                "name": "y",
            },
            "x coord": {
                "name": "x",
            },
            "chunk size": {
                "time": 24,
                "y": 5,
                "x": 4,
            },
            "results archive": {
                "datasets": {
                    "hour": {
                        "surface fields": {},
                    }
                }
            },
        }

        extracted_vars = extract.calc_extracted_vars(
            source_dataset, output_coords, config, model_profile
        )

        assert extracted_vars[0].name == "atmpres"
        assert numpy.array_equal(
            extracted_vars[0].data, numpy.ones((24, 5, 4), dtype=numpy.single)
        )
        assert extracted_vars[0].attrs["standard_name"] == "PRMSL_meansealevel"
        assert extracted_vars[0].attrs["long_name"] == "Pressure Reduced to MSL"
        assert extracted_vars[0].attrs["units"] == "Pa"
        for coord in output_coords:
            assert numpy.array_equal(
                extracted_vars[0].coords[coord], output_coords[coord]
            )

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted atmpres"

    def test_extract_var_time_selection(
        self, source_dataset, model_profile, log_output
    ):
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {
            "dataset": {
                "time base": "hour",
                "variables group": "biology",
            },
            "selection": {
                "time interval": 2,
            },
        }

        extracted_vars = extract.calc_extracted_vars(
            source_dataset, output_coords, config, model_profile
        )

        assert extracted_vars[0].name == "diatoms"
        assert numpy.array_equal(
            extracted_vars[0].data, numpy.ones((2, 8, 9, 4), dtype=numpy.single)
        )
        assert (
            extracted_vars[0].attrs["standard_name"]
            == "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water"
        )
        assert extracted_vars[0].attrs["long_name"] == "Diatoms Concentration"
        assert extracted_vars[0].attrs["units"] == "mmol m-3"
        for coord in output_coords:
            assert numpy.array_equal(
                extracted_vars[0].coords[coord], output_coords[coord]
            )

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted diatoms"

    def test_extract_var_depth_selection(
        self, source_dataset, model_profile, log_output
    ):
        output_coords = {
            "time": numpy.arange(4),
            "depth": numpy.arange(0.5, 3, 1),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {
            "dataset": {
                "time base": "hour",
                "variables group": "biology",
            },
            "selection": {
                "depth": {
                    "depth min": 1,
                    "depth max": 6,
                    "depth interval": 2,
                }
            },
        }

        extracted_vars = extract.calc_extracted_vars(
            source_dataset, output_coords, config, model_profile
        )

        assert extracted_vars[0].name == "diatoms"
        assert numpy.array_equal(
            extracted_vars[0].data, numpy.ones((4, 3, 9, 4), dtype=numpy.single)
        )
        assert (
            extracted_vars[0].attrs["standard_name"]
            == "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water"
        )
        assert extracted_vars[0].attrs["long_name"] == "Diatoms Concentration"
        assert extracted_vars[0].attrs["units"] == "mmol m-3"
        for coord in output_coords:
            assert numpy.array_equal(
                extracted_vars[0].coords[coord], output_coords[coord]
            )

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted diatoms"

    def test_extract_var_y_selection(self, source_dataset, model_profile, log_output):
        output_coords = {
            "time": numpy.arange(4),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(2, 7),
            "gridX": numpy.arange(4),
        }
        config = {
            "dataset": {
                "time base": "hour",
                "variables group": "biology",
            },
            "selection": {
                "grid y": {
                    "y min": 2,
                    "y max": 7,
                }
            },
        }

        extracted_vars = extract.calc_extracted_vars(
            source_dataset, output_coords, config, model_profile
        )

        assert extracted_vars[0].name == "diatoms"
        assert numpy.array_equal(
            extracted_vars[0].data, numpy.ones((4, 8, 5, 4), dtype=numpy.single)
        )
        assert (
            extracted_vars[0].attrs["standard_name"]
            == "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water"
        )
        assert extracted_vars[0].attrs["long_name"] == "Diatoms Concentration"
        assert extracted_vars[0].attrs["units"] == "mmol m-3"
        for coord in output_coords:
            assert numpy.array_equal(
                extracted_vars[0].coords[coord], output_coords[coord]
            )

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted diatoms"

    def test_extract_var_x_selection(self, source_dataset, model_profile, log_output):
        output_coords = {
            "time": numpy.arange(4),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(2, 4),
        }
        config = {
            "dataset": {
                "time base": "hour",
                "variables group": "biology",
            },
            "selection": {
                "grid x": {
                    "x min": 2,
                }
            },
        }

        extracted_vars = extract.calc_extracted_vars(
            source_dataset, output_coords, config, model_profile
        )

        assert extracted_vars[0].name == "diatoms"
        assert numpy.array_equal(
            extracted_vars[0].data, numpy.ones((4, 8, 9, 2), dtype=numpy.single)
        )
        assert (
            extracted_vars[0].attrs["standard_name"]
            == "mole_concentration_of_diatoms_expressed_as_nitrogen_in_sea_water"
        )
        assert extracted_vars[0].attrs["long_name"] == "Diatoms Concentration"
        assert extracted_vars[0].attrs["units"] == "mmol m-3"
        for coord in output_coords:
            assert numpy.array_equal(
                extracted_vars[0].coords[coord], output_coords[coord]
            )

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted diatoms"

    def test_extract_surface_var(self, model_profile, log_output):
        source_dataset = xarray.Dataset(
            coords={
                "time_counter": numpy.arange(4),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "sossheig": xarray.DataArray(
                    name="sossheig",
                    data=numpy.ones((4, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": numpy.arange(4),
                        "y": numpy.arange(9),
                        "x": numpy.arange(4),
                    },
                    attrs={
                        "standard_name": "sea_surface_height_above_geoid",
                        "long_name": "Sea Surface Height",
                        "units": "m",
                    },
                )
            },
        )

        output_coords = {
            "time": numpy.arange(4),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {
            "dataset": {
                "time base": "hour",
                "variables group": "biology",
            },
        }

        extracted_vars = extract.calc_extracted_vars(
            source_dataset, output_coords, config, model_profile
        )

        assert extracted_vars[0].name == "sossheig"
        assert numpy.array_equal(
            extracted_vars[0].data, numpy.ones((4, 9, 4), dtype=numpy.single)
        )
        assert (
            extracted_vars[0].attrs["standard_name"] == "sea_surface_height_above_geoid"
        )
        assert extracted_vars[0].attrs["long_name"] == "Sea Surface Height"
        assert extracted_vars[0].attrs["units"] == "m"
        for coord in output_coords:
            assert numpy.array_equal(
                extracted_vars[0].coords[coord], output_coords[coord]
            )

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted sossheig"


class TestCalcExtractedDataset:
    """Unit tests for calc_extracted_dataset() function."""

    def test_calc_extracted_dataset_no_date_overrides(self, log_output, monkeypatch):
        def mock_now(tz):
            return arrow.get("2022-10-28 19:12", tzinfo="Canada/Pacific")

        monkeypatch.setattr(extract.arrow, "now", mock_now)

        extracted_vars = []
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {
            "start date": datetime.date(2015, 1, 1),
            "end date": datetime.date(2015, 1, 10),
            "extracted dataset": {
                "name": "test",
                "description": "Day-averaged diatoms biomass extracted from SalishSeaCast v201812 hindcast",
            },
        }
        config_yaml = Path("test_extract.yaml")
        generated_by = f"`reshapr extract {config_yaml.absolute()}`"

        extracted_ds = extract.calc_extracted_dataset(
            extracted_vars, output_coords, config, generated_by
        )

        assert extracted_ds.name == "test_20150101_20150110"
        assert extracted_ds.attrs["name"] == "test_20150101_20150110"
        assert (
            extracted_ds.attrs["description"]
            == "Day-averaged diatoms biomass extracted from SalishSeaCast v201812 hindcast"
        )
        assert (
            extracted_ds.attrs["history"]
            == f"2022-10-28 19:12 -07:00: Generated by {generated_by}"
        )
        assert extracted_ds.attrs["Conventions"] == "CF-1.6"

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted dataset metadata"

    def test_calc_extracted_dataset_date_overrides(self, log_output, monkeypatch):
        def mock_now(tz):
            return arrow.get("2022-11-09 15:06", tzinfo="Canada/Pacific")

        monkeypatch.setattr(extract.arrow, "now", mock_now)

        extracted_vars = []
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {
            "start date": datetime.date(2015, 1, 1),
            "end date": datetime.date(2015, 1, 10),
            "extracted dataset": {
                "name": "test",
                "description": "Day-averaged diatoms biomass extracted from SalishSeaCast v201812 hindcast",
            },
        }
        config_yaml = Path("test_extract.yaml")
        generated_by = f"`reshapr extract {config_yaml.absolute()}`"
        override_start_date, override_end_date = "2022-11-09", "2022-11-09"

        extracted_ds = extract.calc_extracted_dataset(
            extracted_vars,
            output_coords,
            config,
            generated_by,
            override_start_date,
            override_end_date,
        )

        assert extracted_ds.name == "test_20221109_20221109"
        assert extracted_ds.attrs["name"] == "test_20221109_20221109"
        assert (
            extracted_ds.attrs["description"]
            == "Day-averaged diatoms biomass extracted from SalishSeaCast v201812 hindcast"
        )
        assert (
            extracted_ds.attrs["history"]
            == f"2022-11-09 15:06 -08:00: Generated by {generated_by}"
        )
        assert extracted_ds.attrs["Conventions"] == "CF-1.6"

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted dataset metadata"


class TestResample:
    """Unit test for _resample() function."""

    def test_resample_day_average(self, log_output, monkeypatch):
        extracted_ds = xarray.Dataset(
            coords={
                "time": pandas.date_range(
                    "2015-04-01",
                    periods=24,
                    freq=pandas.tseries.offsets.DateOffset(hours=1),
                ),
                "depth": numpy.arange(0, 4, 0.5),
                "gridY": numpy.arange(9),
                "gridX": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.empty((24, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time": pandas.date_range(
                            "2015-04-01",
                            periods=24,
                            freq=pandas.tseries.offsets.DateOffset(hours=1),
                        ),
                        "depth": numpy.arange(0, 4, 0.5),
                        "gridY": numpy.arange(9),
                        "gridX": numpy.arange(4),
                    },
                )
            },
            attrs={
                "name": "test_20150401_20150401",
                "description": "Day-averaged diatoms biomass extracted from SalishSeaCast v201905 hindcast",
            },
        )

        config = {
            "start date": datetime.date(2015, 4, 1),
            "end date": datetime.date(2015, 4, 1),
            "resample": {
                "time interval": "1D",
            },
        }
        model_profile = {"extraction time origin": "2007-01-01"}

        resampled_ds = extract._resample(extracted_ds, config, model_profile)

        assert log_output.entries[0]["log_level"] == "info"
        assert log_output.entries[0]["event"] == "resampling dataset"
        assert log_output.entries[0]["resampling_time_interval"] == "1D"
        assert log_output.entries[0]["aggregation"] == "mean"

        assert resampled_ds.name == "test_20150401_20150401"
        assert resampled_ds.attrs["name"] == "test_20150401_20150401"
        assert (
            resampled_ds.attrs["description"]
            == "Day-averaged diatoms biomass extracted from SalishSeaCast v201905 hindcast"
        )
        expected = xarray.DataArray(
            numpy.array([pandas.to_datetime("2015-04-01 12:00:00")]),
            coords={"time": numpy.array([pandas.to_datetime("2015-04-01 12:00:00")])},
            dims="time",
            attrs={
                "standard_name": "time",
                "long_name": "Time Axis",
                "time_origin": "2007-01-01 12:00:00",
                "comment": (
                    "time values are UTC at the centre of the intervals over which the "
                    "calculated model results are averaged; "
                    "e.g. the field average values for 8 February 2022 have "
                    "a time value of 2022-02-08 12:00:00Z"
                ),
            },
        )
        assert resampled_ds.time == expected
        assert resampled_ds.time.attrs == expected.attrs

        assert log_output.entries[1]["log_level"] == "debug"
        assert log_output.entries[1]["event"] == "resampled dataset metadata"

    def test_resample_month_average(self, log_output, monkeypatch):
        extracted_ds = xarray.Dataset(
            coords={
                "time": pandas.date_range(
                    "2015-04-01",
                    periods=30,
                    freq=pandas.tseries.offsets.DateOffset(days=1),
                ),
                "depth": numpy.arange(0, 4, 0.5),
                "gridY": numpy.arange(9),
                "gridX": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.empty((30, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time": pandas.date_range(
                            "2015-04-01",
                            periods=30,
                            freq=pandas.tseries.offsets.DateOffset(days=1),
                        ),
                        "depth": numpy.arange(0, 4, 0.5),
                        "gridY": numpy.arange(9),
                        "gridX": numpy.arange(4),
                    },
                )
            },
            attrs={
                "name": "test_20150401_20150430",
                "description": "Month-averaged diatoms biomass extracted from SalishSeaCast v201905 hindcast",
            },
        )

        config = {
            "start date": datetime.date(2015, 4, 1),
            "end date": datetime.date(2015, 4, 30),
            "resample": {
                "time interval": "1M",
            },
        }
        model_profile = {"extraction time origin": "2007-01-01"}

        resampled_ds = extract._resample(extracted_ds, config, model_profile)

        assert log_output.entries[0]["log_level"] == "info"
        assert log_output.entries[0]["event"] == "resampling dataset"
        assert log_output.entries[0]["resampling_time_interval"] == "1M"
        assert log_output.entries[0]["aggregation"] == "mean"

        assert resampled_ds.name == "test_20150401_20150430"
        assert resampled_ds.attrs["name"] == "test_20150401_20150430"
        assert (
            resampled_ds.attrs["description"]
            == "Month-averaged diatoms biomass extracted from SalishSeaCast v201905 hindcast"
        )
        expected = xarray.DataArray(
            pandas.date_range(
                "2015-04-15", periods=1, freq=pandas.tseries.offsets.DateOffset(days=1)
            ),
            coords={
                "time": pandas.date_range(
                    "2015-04-15",
                    periods=1,
                    freq=pandas.tseries.offsets.DateOffset(days=1),
                )
            },
            dims="time",
            attrs={
                "standard_name": "time",
                "long_name": "Time Axis",
                "time_origin": "2007-01-01 12:00:00",
                "comment": (
                    "time values are UTC at the centre of the intervals over which the "
                    "calculated model results are averaged; "
                    "e.g. the field average values for January 2022 have "
                    "a time value of 2022-01-15 12:00:00Z, "
                    "and those for April 2022 have a time value of 2022-04-15 00:00:00Z"
                ),
            },
        )
        assert resampled_ds.time == expected
        assert resampled_ds.time.attrs == expected.attrs

        assert log_output.entries[1]["log_level"] == "debug"
        assert log_output.entries[1]["event"] == "resampled dataset metadata"


class TestCalcCoordEncoding:
    """Unit tests for calc_coord_encoding() function."""

    @pytest.mark.parametrize(
        "time_base, quanta, time_offset",
        (
            ("day", "days", "12:00:00"),
            ("hour", "hours", "00:30:00"),
            ("fortnight", "seconds", "00:30:00"),  # wildcard pattern test
        ),
    )
    def test_time_coord(self, time_base, quanta, time_offset):
        dataset = xarray.Dataset()
        config = {
            "dataset": {
                "time base": time_base,
            },
            "extracted dataset": {},
        }
        model_profile = {"extraction time origin": "2015-01-01"}

        encoding = extract.calc_coord_encoding(dataset, "time", config, model_profile)

        expected = {
            "dtype": numpy.single,
            "units": f"{quanta} since 2015-01-01 {time_offset}",
            "chunksizes": (1,),
            "zlib": True,
            "_FillValue": None,
        }
        assert encoding == expected

    def test_time_coord_no_deflate(self):
        dataset = xarray.Dataset()
        config = {
            "dataset": {
                "time base": "day",
            },
            "extracted dataset": {"deflate": False},
        }
        model_profile = {"extraction time origin": "2015-01-01"}

        encoding = extract.calc_coord_encoding(dataset, "time", config, model_profile)

        expected = {
            "dtype": numpy.single,
            "units": "days since 2015-01-01 12:00:00",
            "chunksizes": (1,),
            "zlib": False,
            "_FillValue": None,
        }
        assert encoding == expected

    @pytest.mark.parametrize("deflate", (True, False))
    def test_depth_coord(self, deflate):
        dataset = xarray.Dataset(
            coords={
                "depth": numpy.arange(0, 4, 0.5),
            }
        )
        config = {"extracted dataset": {"deflate": deflate}}
        model_profile = {}

        encoding = extract.calc_coord_encoding(dataset, "depth", config, model_profile)

        expected = {
            "dtype": numpy.single,
            "chunksizes": (numpy.arange(0, 4, 0.5).size,),
            "zlib": deflate,
        }
        assert encoding == expected

    @pytest.mark.parametrize(
        "grid_index, deflate",
        (
            ("gridY", True),
            ("gridY", False),
            ("gridX", True),
            ("gridX", False),
        ),
    )
    def test_grid_index_coord(self, grid_index, deflate):
        dataset = xarray.Dataset(
            coords={
                grid_index: numpy.arange(5),
            }
        )
        config = {"extracted dataset": {"deflate": deflate}}
        model_profile = {}

        encoding = extract.calc_coord_encoding(
            dataset, grid_index, config, model_profile
        )

        expected = {
            "dtype": int,
            "chunksizes": (numpy.arange(5).size,),
            "zlib": deflate,
        }
        assert encoding == expected


class TestCalcTimeCoordAttrs:
    """Unit tests for calc_time_coord_attrs() function."""

    @pytest.mark.parametrize(
        "time_base, time_offset, example",
        (
            (
                "hour",
                "00:30:00",
                "e.g. the field average values for the first hour of 8 February 2022 have "
                "a time value of 2022-02-08 00:30:00Z",
            ),
            (
                "day",
                "12:00:00",
                "e.g. the field average values for 8 February 2022 have "
                "a time value of 2022-02-08 12:00:00Z",
            ),
            (
                "month",
                "12:00:00",
                "e.g. the field average values for January 2022 have "
                "a time value of 2022-01-15 12:00:00Z, "
                "and those for April 2022 have a time value of 2022-04-15 00:00:00Z",
            ),
        ),
    )
    def test_calc_time_coord_attrs(self, time_base, time_offset, example):
        model_profile = {"extraction time origin": "2007-01-01"}
        time_attrs = extract.calc_time_coord_attrs(time_base, model_profile)

        expected = {
            "standard_name": "time",
            "long_name": "Time Axis",
            "time_origin": f"2007-01-01 {time_offset}",
            "comment": (
                f"time values are UTC at the centre of the intervals over which the "
                f"calculated model results are averaged; {example}"
            ),
        }
        assert time_attrs == expected

    def test_unrecognized_time_base(self):
        model_profile = {"extraction time origin": "2007-01-01"}
        time_attrs = extract.calc_time_coord_attrs(
            "unusual offset alias", model_profile
        )

        expected = {
            "standard_name": "time",
            "long_name": "Time Axis",
            "time_origin": f"2007-01-01 00:30:00",
            "comment": (
                f"time values are UTC at the centre of the intervals over which the "
                f"calculated model results are averaged"
            ),
        }
        assert time_attrs == expected


class TestCalcVarEncoding:
    """Unit tests for calc_var_encoding() function."""

    @pytest.mark.parametrize("deflate", (True, False))
    def test_4d_var(self, deflate):
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {"extracted dataset": {"deflate": deflate}}
        var = xarray.DataArray(
            name="diatoms",
            data=numpy.empty((2, 8, 9, 4), dtype=numpy.single),
            coords={
                "time": numpy.arange(2),
                "depth": numpy.arange(0, 4, 0.5),
                "gridY": numpy.arange(9),
                "gridX": numpy.arange(4),
            },
        )

        encoding = extract.calc_var_encoding(var, output_coords, config)

        expected = {
            "dtype": numpy.single,
            "chunksizes": (1, 8, 9, 4),
            "zlib": deflate,
        }
        assert encoding == expected

    @pytest.mark.parametrize("deflate", (True, False))
    def test_2d_var(self, deflate):
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {"extracted dataset": {"deflate": deflate}}
        var = xarray.DataArray(
            name="longitude",
            data=numpy.empty((9, 4), dtype=numpy.single),
            coords={
                "gridY": numpy.arange(9),
                "gridX": numpy.arange(4),
            },
        )

        encoding = extract.calc_var_encoding(var, output_coords, config)

        expected = {
            "dtype": numpy.single,
            "chunksizes": (9, 4),
            "zlib": deflate,
        }
        assert encoding == expected


class TestPrepNetcdfWrite:
    """Unit test for prep_netcdf_write() function."""

    def test_nc_path(self, log_output, tmp_path):
        extracted_ds = xarray.Dataset(
            attrs={"name": "test"},
        )
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        dest_dir = tmp_path / "dest_dir"
        dest_dir.mkdir()
        config = {
            "extracted dataset": {
                "dest dir": os.fspath(dest_dir),
                "name": f"{extracted_ds.name}.nc",
            }
        }
        model_profile = {}

        nc_path, _, _ = extract.prep_netcdf_write(
            extracted_ds, output_coords, config, model_profile
        )

        assert nc_path == dest_dir / f"{extracted_ds.name}.nc"

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "prepared netCDF4 write params"
        assert log_output.entries[0]["nc_path"] == dest_dir / f"{extracted_ds.name}.nc"

    def test_encoding(self, log_output, tmp_path):
        extracted_ds = xarray.Dataset(
            coords={
                "time": numpy.arange(2),
                "depth": numpy.arange(0, 4, 0.5),
                "gridY": numpy.arange(9),
                "gridX": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.empty((2, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time": numpy.arange(2),
                        "depth": numpy.arange(0, 4, 0.5),
                        "gridY": numpy.arange(9),
                        "gridX": numpy.arange(4),
                    },
                )
            },
            attrs={"name": "test"},
        )
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        dest_dir = tmp_path / "dest_dir"
        dest_dir.mkdir()
        config = {
            "dataset": {
                "time base": "day",
            },
            "extracted dataset": {
                "dest dir": os.fspath(dest_dir),
                "name": f"{extracted_ds.name}.nc",
            },
        }
        model_profile = {"extraction time origin": "2015-01-01"}

        _, encoding, _ = extract.prep_netcdf_write(
            extracted_ds, output_coords, config, model_profile
        )

        expected = {
            "time": {
                "dtype": numpy.single,
                "units": "days since 2015-01-01 12:00:00",
                "chunksizes": (1,),
                "zlib": True,
                "_FillValue": None,
            },
            "depth": {
                "dtype": numpy.single,
                "chunksizes": (numpy.arange(0, 4, 0.5).size,),
                "zlib": True,
            },
            "gridY": {
                "dtype": int,
                "chunksizes": (numpy.arange(9).size,),
                "zlib": True,
            },
            "gridX": {
                "dtype": int,
                "chunksizes": (numpy.arange(4).size,),
                "zlib": True,
            },
            "diatoms": {
                "dtype": numpy.single,
                "chunksizes": (1, 8, 9, 4),
                "zlib": True,
            },
        }
        assert encoding == expected

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "prepared netCDF4 write params"
        assert log_output.entries[0]["encoding"] == expected

    @pytest.mark.parametrize(
        "format, expected",
        (
            ("NETCDF4", "NETCDF4"),
            ("NETCDF4_CLASSIC", "NETCDF4_CLASSIC"),
            ("NETCDF3_64BIT", "NETCDF3_64BIT"),
            ("NETCDF3_CLASSIC", "NETCDF3_CLASSIC"),
        ),
    )
    def test_nc_format(self, format, expected, log_output, tmp_path):
        extracted_ds = xarray.Dataset(
            attrs={"name": "test"},
        )
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        dest_dir = tmp_path / "dest_dir"
        dest_dir.mkdir()
        config = {
            "extracted dataset": {
                "dest dir": os.fspath(dest_dir),
                "name": f"{extracted_ds.name}.nc",
                "format": format,
            }
        }
        model_profile = {}

        _, _, nc_format = extract.prep_netcdf_write(
            extracted_ds, output_coords, config, model_profile
        )

        assert nc_format == expected

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "prepared netCDF4 write params"
        assert log_output.entries[0]["nc_format"] == expected

    def test_default_nc_format(self, log_output, tmp_path):
        extracted_ds = xarray.Dataset(
            attrs={"name": "test"},
        )
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        dest_dir = tmp_path / "dest_dir"
        dest_dir.mkdir()
        config = {
            "extracted dataset": {
                "dest dir": os.fspath(dest_dir),
                "name": f"{extracted_ds.name}.nc",
            }
        }
        model_profile = {}

        _, _, nc_format = extract.prep_netcdf_write(
            extracted_ds, output_coords, config, model_profile
        )

        assert nc_format == "NETCDF4"

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "prepared netCDF4 write params"
        assert log_output.entries[0]["nc_format"] == "NETCDF4"
