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
import os
import textwrap
from pathlib import Path

import arrow
import numpy
import pytest
import xarray

from reshapr.core import extract


class TestLoadConfig:
    """Unit tests for core.extract._load_config() function."""

    def test_load_config(self, log_output, tmp_path):
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

        config = extract._load_config(extract_config_yaml)

        assert config["dask cluster"] == "docs/subcommands/salish_cluster.yaml"

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["config_file"] == os.fspath(extract_config_yaml)
        assert log_output.entries[0]["event"] == "loaded config"

    def test_no_config_file(self, log_output, tmp_path):
        nonexistent_config_yaml = tmp_path / "nonexistent.yaml"

        with pytest.raises(SystemExit) as exc_info:
            extract._load_config(nonexistent_config_yaml)

        assert exc_info.value.code == 2
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["config_file"] == os.fspath(
            nonexistent_config_yaml
        )
        assert log_output.entries[0]["event"] == "config file not found"


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

        assert log_output.entries[0]["log_level"] == "debug"
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

        assert model_profile["name"] == "SalishSeaCast.201812"

        assert log_output.entries[0]["log_level"] == "debug"
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


class Test_ddmmmyy:
    """Unit test for ddmmmyy() function."""

    def test_ddmmmyy(self):
        ddmmmyy = extract.ddmmmyy(arrow.get("2022-02-07"))

        assert ddmmmyy == "07feb22"


class Test_yyyymmdd:
    """Unit test for yyyymmdd() function."""

    def test_yyyymmdd(self):
        yyyymmdd = extract.yyyymmdd(arrow.get("2022-02-07"))

        assert yyyymmdd == "20220207"


class Test_nemo_yyyymmdd:
    """Unit test for yyyymmdd() function."""

    def test_nemo_yyyymmdd(self):
        nemo_yyyymmdd = extract.nemo_yyyymmdd(arrow.get("2022-02-28"))

        assert nemo_yyyymmdd == "y2022m02d28"


class TestCalcDsPaths:
    """Unit tests for calc_ds_paths() function."""

    def test_SalishSeaCast_ds_paths(self, log_output):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "start date": "2015-01-01",
            "end date": "2015-01-02",
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
            "start date": "2015-01-01",
            "end date": "2015-01-02",
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
            "start date": "2015-01-01",
            "end date": "2015-01-02",
        }
        model_profile = {
            "time coord": "time_counter",
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
            "start date": "2015-01-01",
            "end date": "2015-01-02",
        }
        model_profile = {
            "time coord": "time_counter",
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


class TestCalcOutputCoords:
    "Unit tests for calc_output_coords() function."

    @pytest.fixture(name="model_profile", scope="class")
    def fixture_model_profile(self):
        return {
            "time coord": "time_counter",
            "y coord": "y",
            "x coord": "x",
            "chunk size": {
                "time": 1,
                "depth": 40,
                "y": 898,
                "x": 398,
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
        "time_base, example",
        (
            ("day", "8 February 2022 have a time value of 2022-02-08 12:00:00Z"),
            (
                "hour",
                "the first hour of 8 February 2022 have a time value of 2022-02-08 00:30:00Z",
            ),
        ),
    )
    def test_time_coord(
        self, time_base, example, source_dataset, model_profile, log_output
    ):
        extract_config = {
            "dataset": {
                "time base": time_base,
                "variables group": "biology",
            }
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["time"].name == "time"
        assert numpy.array_equal(
            output_coords["time"].data, source_dataset.time_counter.data
        )
        assert output_coords["time"].attrs["standard_name"] == "time"
        assert output_coords["time"].attrs["long_name"] == "Time Axis"
        expected = (
            f"time values are UTC at the centre of the intervals over which the "
            f"calculated model results are averaged; e.g. the field average values for "
            f"{example}"
        )
        assert output_coords["time"].attrs["comment"] == expected

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

    def test_no_depth_coord(self):
        model_profile = {
            "time coord": "time_counter",
            "y coord": "y",
            "x coord": "x",
            "chunk size": {
                "time": 24,
                "y": 266,
                "x": 256,
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
            }
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert "depth" not in output_coords

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
            }
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert "depth" not in output_coords

    def test_depth_coord(self, source_dataset, model_profile, log_output):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            }
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["depth"].name == "depth"
        assert numpy.array_equal(
            output_coords["depth"].data, source_dataset.deptht.data
        )
        assert output_coords["depth"].attrs["standard_name"] == "sea_floor_depth"
        assert output_coords["depth"].attrs["long_name"] == "Sea Floor Depth"
        assert output_coords["depth"].attrs["units"] == "metres"
        assert output_coords["depth"].attrs["positive"] == "down"

        assert log_output.entries[1]["log_level"] == "debug"
        assert log_output.entries[1]["event"] == "extraction depth coordinate"

    def test_depth_coord_depth_min(self, source_dataset, model_profile):
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
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["depth"].name == "depth"
        assert numpy.array_equal(
            output_coords["depth"].data,
            source_dataset.deptht.isel(deptht=slice(5, 901)),
        )

    def test_depth_coord_depth_max(self, source_dataset, model_profile):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            },
            "selection": {
                "depth": {
                    "depth max": 25,
                },
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["depth"].name == "depth"
        assert numpy.array_equal(
            output_coords["depth"].data, source_dataset.deptht.isel(deptht=slice(0, 25))
        )

    def test_depth_coord_depth_interval(self, source_dataset, model_profile):
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
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["depth"].name == "depth"
        assert numpy.array_equal(
            output_coords["depth"].data,
            source_dataset.deptht.isel(deptht=slice(0, 901, 2)),
        )

    def test_y_index_coord(self, source_dataset, model_profile, log_output):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            }
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(output_coords["gridY"].data, source_dataset.y.data)
        assert output_coords["gridY"].attrs["standard_name"] == "y"
        assert output_coords["gridY"].attrs["long_name"] == "Grid Y"
        assert output_coords["gridY"].attrs["units"] == "count"
        assert (
            output_coords["gridY"].attrs["comment"]
            == "gridY values are grid indices in the model y-direction"
        )

        assert log_output.entries[2]["log_level"] == "debug"
        assert log_output.entries[2]["event"] == "extraction y coordinate"

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
                    "y min": 600,
                },
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(
            output_coords["gridY"].data, source_dataset.y.isel(y=slice(600, 898))
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
                    "y max": 300,
                },
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(
            output_coords["gridY"].data, source_dataset.y.isel(y=slice(0, 300))
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
                    "y interval": 10,
                },
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridY"].name == "gridY"
        assert numpy.array_equal(
            output_coords["gridY"].data, source_dataset.y.isel(y=slice(0, 898, 10))
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

    def test_x_index_coord(self, source_dataset, model_profile, log_output):
        extract_config = {
            "dataset": {
                "time base": "day",
                "variables group": "biology",
            }
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        assert numpy.array_equal(output_coords["gridX"].data, source_dataset.x.data)
        assert output_coords["gridX"].attrs["standard_name"] == "x"
        assert output_coords["gridX"].attrs["long_name"] == "Grid X"
        assert output_coords["gridX"].attrs["units"] == "count"
        assert (
            output_coords["gridX"].attrs["comment"]
            == "gridX values are grid indices in the model x-direction"
        )

        assert log_output.entries[3]["log_level"] == "debug"
        assert log_output.entries[3]["event"] == "extraction x coordinate"

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
                    "x min": 100,
                },
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        assert numpy.array_equal(
            output_coords["gridX"].data, source_dataset.x.isel(x=slice(100, 398))
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
                    "x max": 300,
                },
            },
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        assert numpy.array_equal(
            output_coords["gridX"].data, source_dataset.x.isel(x=slice(0, 300))
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
        }

        output_coords = extract.calc_output_coords(
            source_dataset, extract_config, model_profile
        )

        assert output_coords["gridX"].name == "gridX"
        assert numpy.array_equal(
            output_coords["gridX"].data, source_dataset.x.isel(x=slice(0, 398, 2))
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
            "time coord": "time_counter",
            "y coord": "y",
            "x coord": "x",
            "chunk size": {
                "time": 24,
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
                        "standard_name": "PRMSL_meansealevel",
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
            "time coord": "time_counter",
            "y coord": "y",
            "x coord": "x",
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
    """Unit test for calc_extracted_dataset() function."""

    def test_calc_extracted_dataset(self, log_output, monkeypatch):
        def mock_now(tz):
            return arrow.get("2022-02-09 15:50")

        monkeypatch.setattr(extract.arrow, "now", mock_now)

        extracted_vars = []
        output_coords = {
            "time": numpy.arange(2),
            "depth": numpy.arange(0, 4, 0.5),
            "gridY": numpy.arange(9),
            "gridX": numpy.arange(4),
        }
        config = {
            "start date": "2015-01-01",
            "end date": "2015-01-10",
            "extracted dataset": {
                "name": "test",
                "description": "Day-averaged diatoms biomass extracted from SalishSeaCast v201812 hindcast",
            },
        }
        config_yaml = Path("test_extract.yaml")

        extracted_ds = extract.calc_extracted_dataset(
            extracted_vars, output_coords, config, config_yaml
        )

        assert extracted_ds.name == "test_20150101_20150110"
        assert extracted_ds.attrs["name"] == "test_20150101_20150110"
        assert (
            extracted_ds.attrs["description"]
            == "Day-averaged diatoms biomass extracted from SalishSeaCast v201812 hindcast"
        )
        assert (
            extracted_ds.attrs["history"]
            == "2022-02-09 15:50: Generated by `reshapr extract test_extract.yaml`"
        )
        assert extracted_ds.attrs["Conventions"] == "CF-1.6"

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["event"] == "extracted dataset metadata"


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
