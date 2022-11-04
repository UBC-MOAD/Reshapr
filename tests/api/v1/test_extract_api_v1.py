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
import textwrap

import arrow
import pytest

from reshapr.api.v1 import extract


class TestExtractDataset:
    """Unit test for api.v1.extract.extract_dataset() function."""

    def test_extract_dataset(self):
        with pytest.raises(NotImplementedError):
            extract.extract_dataset()


class TestExtractNetcdf:
    """Unit test for api.v1.extract.extract_netcdf() function."""

    def test_extract_netcdf(self):
        with pytest.raises(NotImplementedError):
            extract.extract_netcdf()


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
