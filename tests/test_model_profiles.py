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


"""Tests for package-supplied model profile YAML files.
"""
from pathlib import Path

import pytest
import yaml

MODEL_PROFILES_DIR = Path(__file__).parent.parent / "model_profiles"
MODEL_PROFILES = (
    Path("SalishSeaCast-201812.yaml"),
    Path("unused-variables.yaml"),
)


class TestModelProfiles:
    """Tests of model profile YAML files."""

    def test_model_profiles_coverage(self):
        model_profiles = set(MODEL_PROFILES_DIR / profile for profile in MODEL_PROFILES)
        assert set(MODEL_PROFILES_DIR.glob("*.yaml")) == model_profiles

    @pytest.mark.parametrize("model_profile_yaml", MODEL_PROFILES)
    def test_required_items(self, model_profile_yaml):
        if model_profile_yaml == Path("unused-variables.yaml"):
            # unused-variables.yaml isn't a model profile, it just lives with them
            return
        with (MODEL_PROFILES_DIR / model_profile_yaml).open("rt") as f:
            model_profile = yaml.safe_load(f)

        assert model_profile["name"] is not None
        assert model_profile["results archive"] is not None
        assert model_profile["results archive"]["path"] is not None
        assert model_profile["results archive"]["datasets"] is not None
        assert model_profile["time coord"] is not None
        assert model_profile["chunk size"] is not None

    def test_unused_variables(self):
        with (MODEL_PROFILES_DIR / "unused-variables.yaml").open("rt") as f:
            unused_vars = yaml.safe_load(f)

        expected = [
            "time_centered",
            "nav_lon",
            "nav_lat",
        ]
        assert unused_vars == expected


class TestSalishSeaCast201812:
    """Test of contents of SalishSeaCast-201812 model profile YAML."""

    def test_SalishSeaCast_201812(self):
        with (MODEL_PROFILES_DIR / "SalishSeaCast-201812.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)

        assert model_profile["name"] == "SalishSeaCast.201812"
        assert (
            model_profile["results archive"]["path"]
            == "/results/SalishSea/nowcast-green.201812/"
        )
        assert model_profile["time coord"] == "time_counter"
        expected_chunk_size = {
            "time": 1,
            "depth": 40,
            "y": 898,
            "x": 398,
        }
        assert model_profile["chunk size"] == expected_chunk_size

    @pytest.mark.parametrize(
        "var_group, file_pattern, depth_coord",
        (
            ("auxiliary", "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_carp_T.nc", "deptht"),
            ("biology", "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc", "deptht"),
            ("chemistry", "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_carp_T.nc", "deptht"),
            (
                "grazing and mortality",
                "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_dia2_T.nc",
                "deptht",
            ),
            (
                "physics tracers",
                "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_T.nc",
                "deptht",
            ),
            ("u velocity", "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_U.nc", "depthu"),
            ("v velocity", "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_V.nc", "depthv"),
            (
                "vertical turbulence",
                "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
            ("w velocity", "SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_W.nc", "depthw"),
        ),
    )
    def test_SalishSeaCast_201812_day_datasets(
        self, var_group, file_pattern, depth_coord
    ):
        with (MODEL_PROFILES_DIR / "SalishSeaCast-201812.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)
        day_datasets = model_profile["results archive"]["datasets"]["day"]

        assert day_datasets[var_group]["file pattern"] == file_pattern
        assert day_datasets[var_group]["depth coord"] == depth_coord

    @pytest.mark.parametrize(
        "var_group, file_pattern, depth_coord",
        (
            ("auxiliary", "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_carp_T.nc", "deptht"),
            ("biology", "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc", "deptht"),
            ("chemistry", "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_carp_T.nc", "deptht"),
            (
                "physics tracers",
                "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_T.nc",
                "deptht",
            ),
            (
                "primary production",
                "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_prod_T.nc",
                "deptht",
            ),
            ("u velocity", "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_U.nc", "depthu"),
            ("v velocity", "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_V.nc", "depthv"),
            (
                "vertical turbulence",
                "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
            ("w velocity", "SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_W.nc", "depthw"),
        ),
    )
    def test_SalishSeaCast_201812_hour_datasets(
        self, var_group, file_pattern, depth_coord
    ):
        with (MODEL_PROFILES_DIR / "SalishSeaCast-201812.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)
        hour_datasets = model_profile["results archive"]["datasets"]["hour"]

        assert hour_datasets[var_group]["file pattern"] == file_pattern
        assert hour_datasets[var_group]["depth coord"] == depth_coord
