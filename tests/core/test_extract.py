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
import pytest

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

        assert exc_info.value.code == 1
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

        assert exc_info.value.code == 1
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["model_profile_yaml"] == os.fspath(
            nonexistent_model_profile_yaml
        )
        assert log_output.entries[0]["event"] == "model profile file not found"

    def test_no_model_profile_in_model_profiles_dir(self, log_output):
        nonexistent_model_profile_yaml = Path("nonexistent.yaml")

        with pytest.raises(SystemExit) as exc_info:
            extract._load_model_profile(nonexistent_model_profile_yaml)

        assert exc_info.value.code == 1
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

        assert exc_info.value.code == 1
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


class TestCalcDsPaths:
    """Unit test for calc_ds_paths() function."""

    def test_calc_ds_paths(self, log_output):
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
                            "file pattern": "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
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
            == "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
        )
        assert log_output.entries[0]["start_date"] == "2015-01-01"
        assert log_output.entries[0]["end_date"] == "2015-01-02"
        assert log_output.entries[0]["n_datasets"] == 2
        assert log_output.entries[0]["event"] == "collected dataset paths"


class TestCalcDsChunks:
    """Unit test for calc_ds_chunk() function."""

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
