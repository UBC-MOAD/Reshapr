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


"""Unit test for v1 extraction API functions.
"""
import datetime
import os
import textwrap

import arrow
import numpy
import pandas
import pytest
import xarray
import yaml

from reshapr.api.v1 import extract


class TestExtractDataset:
    """Unit test for api.v1.extract.extract_dataset() function."""

    def test_extract_dataset(self):
        with pytest.raises(NotImplementedError):
            extract.extract_dataset()


class TestExtractNetcdf:
    """Unit test for api.v1.extract.extract_netcdf() function."""

    def test_climatology_resample_conflict(self, log_output, tmp_path):
        config_yaml = tmp_path / "test_extract_config.yaml"
        config_yaml.write_text(
            textwrap.dedent(
                f"""\
                dataset:
                  model profile: {tmp_path / "test_profile.yaml"}
                  time base: hour
                  variables group: biology

                dask cluster: unit_test_cluster.yaml

                start date: 2015-04-01
                end date: 2015-04-01

                extract variables:
                  - diatoms

                resample:
                  time interval: 1D

                climatology:
                  group by: 1D

                extracted dataset:
                  name: SalishSeaCast_1d_diatoms
                  description: Day-averaged diatoms extracted from v202111 SalishSea_1h_*_biol_T.nc
                  dest dir: {tmp_path}
                """
            )
        )
        with config_yaml.open("rt") as f:
            config = yaml.safe_load(f)

        with pytest.raises(ValueError) as exc_info:
            extract.extract_netcdf(config, config_yaml)

        expected = (
            "`resample` and `climatology` in the same extraction is not supported"
        )
        assert exc_info.value.args[0] == expected
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["config_file"] == os.fspath(config_yaml)
        assert log_output.entries[0]["event"] == expected

    def test_extract_netcdf(self, tmp_path):
        test_ds = xarray.Dataset(
            coords={
                "time_counter": pandas.date_range(
                    "2015-04-01",
                    periods=24,
                    freq=pandas.tseries.offsets.DateOffset(hours=1),
                ),
                "deptht": numpy.arange(0, 4, 0.5),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.ones((24, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": pandas.date_range(
                            "2015-04-01",
                            periods=24,
                            freq=pandas.tseries.offsets.DateOffset(hours=1),
                        ),
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
            attrs={
                "name": "SalishSea_1h_20150401_20150401",
                "description": "biology",
            },
        )
        encoding = {
            "time_counter": {
                "dtype": numpy.single,
                "units": "days since 2007-01-01 12:00:00",
                "chunksizes": (24,),
                "zlib": True,
                "_FillValue": None,
            },
            "deptht": {
                "dtype": numpy.single,
                "chunksizes": (numpy.arange(0, 4, 0.5).size,),
                "zlib": True,
            },
            "y": {
                "dtype": int,
                "chunksizes": (numpy.arange(9).size,),
                "zlib": True,
            },
            "x": {
                "dtype": int,
                "chunksizes": (numpy.arange(4).size,),
                "zlib": True,
            },
            "diatoms": {
                "dtype": numpy.single,
                "chunksizes": (24, 8, 9, 4),
                "zlib": True,
            },
        }
        test_ds.to_netcdf(
            tmp_path / "SalishSea_1h_20150401_20150401_biol_T.nc",
            format="NETCDF4",
            encoding=encoding,
            unlimited_dims="time_counter",
            engine="netcdf4",
        )

        model_profile_yaml = tmp_path / "test_profile.yaml"
        model_profile_yaml.write_text(
            textwrap.dedent(
                f"""\
                description: model profile for test

                time coord:
                  name: time_counter
                y coord:
                  name: y
                x coord:
                  name: x

                chunk size:
                  time: 24
                  depth: 8
                  y: 9
                  x: 4

                extraction time origin: 2007-01-01

                results archive:
                  path: {tmp_path}
                  datasets:
                    hour:
                      biology:
                        file pattern: "SalishSea_1h_{{yyyymmdd}}_{{yyyymmdd}}_biol_T.nc"
                        depth coord: deptht
                """
            )
        )

        config_yaml = tmp_path / "test_extract_config.yaml"
        config_yaml.write_text(
            textwrap.dedent(
                f"""\
                dataset:
                  model profile: {tmp_path / "test_profile.yaml"}
                  time base: hour
                  variables group: biology

                dask cluster: unit_test_cluster.yaml

                start date: 2015-04-01
                end date: 2015-04-01

                extract variables:
                  - diatoms

                extracted dataset:
                  name: SalishSeaCast_1h_diatoms
                  description: Hour-averaged diatoms extracted from v202111 SalishSea_1h_*_biol_T.nc
                  dest dir: {tmp_path}
                """
            )
        )
        with config_yaml.open("rt") as f:
            config = yaml.safe_load(f)

        nc_path = extract.extract_netcdf(config, config_yaml)

        assert nc_path == tmp_path / "SalishSeaCast_1h_diatoms_20150401_20150401.nc"

    def test_extract_netcdf_with_resampling(self, tmp_path):
        test_ds = xarray.Dataset(
            coords={
                "time_counter": pandas.date_range(
                    "2015-04-01",
                    periods=24,
                    freq=pandas.tseries.offsets.DateOffset(hours=1),
                ),
                "deptht": numpy.arange(0, 4, 0.5),
                "y": numpy.arange(9),
                "x": numpy.arange(4),
            },
            data_vars={
                "diatoms": xarray.DataArray(
                    name="diatoms",
                    data=numpy.ones((24, 8, 9, 4), dtype=numpy.single),
                    coords={
                        "time_counter": pandas.date_range(
                            "2015-04-01",
                            periods=24,
                            freq=pandas.tseries.offsets.DateOffset(hours=1),
                        ),
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
            attrs={
                "name": "SalishSea_1h_20150401_20150401",
                "description": "biology",
            },
        )
        encoding = {
            "time_counter": {
                "dtype": numpy.single,
                "units": "days since 2007-01-01 12:00:00",
                "chunksizes": (24,),
                "zlib": True,
                "_FillValue": None,
            },
            "deptht": {
                "dtype": numpy.single,
                "chunksizes": (numpy.arange(0, 4, 0.5).size,),
                "zlib": True,
            },
            "y": {
                "dtype": int,
                "chunksizes": (numpy.arange(9).size,),
                "zlib": True,
            },
            "x": {
                "dtype": int,
                "chunksizes": (numpy.arange(4).size,),
                "zlib": True,
            },
            "diatoms": {
                "dtype": numpy.single,
                "chunksizes": (24, 8, 9, 4),
                "zlib": True,
            },
        }
        test_ds.to_netcdf(
            tmp_path / "SalishSea_1h_20150401_20150401_biol_T.nc",
            format="NETCDF4",
            encoding=encoding,
            unlimited_dims="time_counter",
            engine="netcdf4",
        )

        model_profile_yaml = tmp_path / "test_profile.yaml"
        model_profile_yaml.write_text(
            textwrap.dedent(
                f"""\
                description: model profile for test

                time coord:
                  name: time_counter
                y coord:
                  name: y
                x coord:
                  name: x

                chunk size:
                  time: 24
                  depth: 8
                  y: 9
                  x: 4

                extraction time origin: 2007-01-01

                results archive:
                  path: {tmp_path}
                  datasets:
                    hour:
                      biology:
                        file pattern: "SalishSea_1h_{{yyyymmdd}}_{{yyyymmdd}}_biol_T.nc"
                        depth coord: deptht
                """
            )
        )

        config_yaml = tmp_path / "test_extract_config.yaml"
        config_yaml.write_text(
            textwrap.dedent(
                f"""\
                dataset:
                  model profile: {tmp_path / "test_profile.yaml"}
                  time base: hour
                  variables group: biology

                dask cluster: unit_test_cluster.yaml

                start date: 2015-04-01
                end date: 2015-04-01

                extract variables:
                  - diatoms

                resample:
                  time interval: 1D
                  aggregation: mean

                extracted dataset:
                  name: SalishSeaCast_1d_diatoms
                  description: Day-averaged diatoms extracted from v202111 SalishSea_1h_*_biol_T.nc
                  dest dir: {tmp_path}
                """
            )
        )
        with config_yaml.open("rt") as f:
            config = yaml.safe_load(f)

        nc_path = extract.extract_netcdf(config, config_yaml)

        assert nc_path == tmp_path / "SalishSeaCast_1d_diatoms_20150401_20150401.nc"


class TestLoadExtractionConfig:
    """Unit tests for api.v1.extract.load_extraction_config() function."""

    def test_load_extraction_config(self, tmp_path):
        config_yaml = tmp_path / "test_extract_config.yaml"
        config_yaml.write_text(
            textwrap.dedent(
                """\
                dataset:
                  model profile: SalishSeaCast-202111-salish.yaml
                  time base: hour
                  variables group: biology

                dask cluster: salish_cluster.yaml

                start date: 2007-01-01
                end date: 2007-01-31

                extract variables:
                  - nitrate

                extracted dataset:
                  name: SalishSeaCast_1h_nitrate
                  description: Hour-averaged nitrate extracted from SalishSeaCast v202111 hindcast
                  dest dir: /ocean/dlatorne/
                """
            )
        )

        config = extract.load_extraction_config(config_yaml)

        assert config["dataset"]["model profile"] == "SalishSeaCast-202111-salish.yaml"
        assert config["dataset"]["time base"] == "hour"
        assert config["dask cluster"] == "salish_cluster.yaml"
        assert config["start date"] == datetime.date(2007, 1, 1)
        assert config["end date"] == datetime.date(2007, 1, 31)
        assert config["extract variables"] == ["nitrate"]
        assert config["extracted dataset"]["name"] == "SalishSeaCast_1h_nitrate"
        expected = "Hour-averaged nitrate extracted from SalishSeaCast v202111 hindcast"
        assert config["extracted dataset"]["description"] == expected
        assert config["extracted dataset"]["dest dir"] == "/ocean/dlatorne/"

    def test_no_config_yaml(self, tmp_path):
        nonexistent_config_yaml = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            extract.load_extraction_config(nonexistent_config_yaml)

    @pytest.mark.parametrize(
        "start_date, end_date, expected_start_date, expected_end_date",
        (
            (
                arrow.get("2022-11-04"),
                None,
                datetime.date(2022, 11, 4),
                datetime.date(2007, 1, 31),
            ),
            (
                None,
                arrow.get("2022-11-04"),
                datetime.date(2007, 1, 1),
                datetime.date(2022, 11, 4),
            ),
            (
                arrow.get("2022-11-04"),
                "2022-11-05",
                datetime.date(2022, 11, 4),
                datetime.date(2022, 11, 5),
            ),
        ),
    )
    def test_override_start_end_dates(
        self, start_date, end_date, expected_start_date, expected_end_date, tmp_path
    ):
        config_yaml = tmp_path / "test_extract_config.yaml"
        config_yaml.write_text(
            textwrap.dedent(
                """\
                start date: 2007-01-01
                end date: 2007-01-31
                """
            )
        )

        config = extract.load_extraction_config(config_yaml, start_date, end_date)

        assert config["start date"] == expected_start_date
        assert config["end date"] == expected_end_date
