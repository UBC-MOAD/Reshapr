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

import arrow
import pytest
import yaml

MODEL_PROFILES_DIR = Path(__file__).parent.parent / "model_profiles"
MODEL_PROFILES = (
    Path("SalishSeaCast-201812.yaml"),
    Path("SalishSeaCast-201905.yaml"),
    Path("HRDPS-2.5km-operational.yaml"),
    Path("HRDPS-2.5km-GEMLAM-pre22sep11.yaml"),
    Path("HRDPS-2.5km-GEMLAM-22sep11onward.yaml"),
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
        assert model_profile["time coord"]["name"] is not None
        assert model_profile["y coord"]["name"] is not None
        assert model_profile["x coord"]["name"] is not None
        assert model_profile["chunk size"] is not None
        assert model_profile["geo ref dataset"]["path"] is not None
        assert model_profile["geo ref dataset"]["y coord"] is not None
        assert model_profile["geo ref dataset"]["x coord"] is not None
        assert model_profile["extraction time origin"] is not None
        assert model_profile["results archive"]["path"] is not None
        assert model_profile["results archive"]["datasets"] is not None

    def test_unused_variables(self):
        with (MODEL_PROFILES_DIR / "unused-variables.yaml").open("rt") as f:
            unused_vars = yaml.safe_load(f)

        expected = [
            "time_centered",
            "nav_lon",
            "nav_lat",
            "bounds_lat",
            "bounds_lon",
            "deptht_bounds",
            "depthu_bounds",
            "depthv_bounds",
            "depthw_bounds",
            "time_centered_bounds",
            "time_counter_bounds",
            "area",
        ]
        assert unused_vars == expected


class TestSalishSeaCast201812:
    """Tests of contents of SalishSeaCast-201812 model profile YAML."""

    def test_SalishSeaCast_201812(self):
        with (MODEL_PROFILES_DIR / "SalishSeaCast-201812.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)

        assert model_profile["name"] == "SalishSeaCast.201812"
        assert model_profile["time coord"]["name"] == "time_counter"
        assert model_profile["y coord"]["name"] == "y"
        assert "units" not in model_profile["y coord"]
        assert "comment" not in model_profile["y coord"]
        assert model_profile["x coord"]["name"] == "x"
        assert "units" not in model_profile["x coord"]
        assert "comment" not in model_profile["x coord"]
        expected_chunk_size = {
            "time": 1,
            "depth": 40,
            "y": 898,
            "x": 398,
        }
        assert model_profile["chunk size"] == expected_chunk_size
        assert (
            model_profile["geo ref dataset"]["path"]
            == "https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSnBathymetryV17-02"
        )
        assert model_profile["geo ref dataset"]["y coord"] == "gridY"
        assert model_profile["geo ref dataset"]["x coord"] == "gridX"
        assert model_profile["extraction time origin"] == arrow.get("2015-01-01").date()
        assert (
            model_profile["results archive"]["path"]
            == "/results/SalishSea/nowcast-green.201812/"
        )

    @pytest.mark.parametrize(
        "var_group, file_pattern, depth_coord",
        (
            (
                "auxiliary",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "biology",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc",
                "deptht",
            ),
            (
                "chemistry",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "grazing and mortality",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_dia2_T.nc",
                "deptht",
            ),
            (
                "physics tracers",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_T.nc",
                "deptht",
            ),
            (
                "u velocity",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_U.nc",
                "depthu",
            ),
            (
                "v velocity",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_V.nc",
                "depthv",
            ),
            (
                "vertical turbulence",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
            (
                "w velocity",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
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
            (
                "auxiliary",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "biology",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc",
                "deptht",
            ),
            (
                "chemistry",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "physics tracers",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_T.nc",
                "deptht",
            ),
            (
                "primary production",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_prod_T.nc",
                "deptht",
            ),
            (
                "u velocity",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_U.nc",
                "depthu",
            ),
            (
                "v velocity",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_V.nc",
                "depthv",
            ),
            (
                "vertical turbulence",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
            (
                "w velocity",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
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


class TestSalishSeaCast201905:
    """Tests of contents of SalishSeaCast-201905 model profile YAML."""

    def test_SalishSeaCast_201905(self):
        with (MODEL_PROFILES_DIR / "SalishSeaCast-201905.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)

        assert model_profile["name"] == "SalishSeaCast.201905"
        assert model_profile["time coord"]["name"] == "time_counter"
        assert model_profile["y coord"]["name"] == "y"
        assert "units" not in model_profile["y coord"]
        assert "comment" not in model_profile["y coord"]
        assert model_profile["x coord"]["name"] == "x"
        assert "units" not in model_profile["x coord"]
        assert "comment" not in model_profile["x coord"]
        expected_chunk_size = {
            "time": 1,
            "depth": 40,
            "y": 898,
            "x": 398,
        }
        assert model_profile["chunk size"] == expected_chunk_size
        assert (
            model_profile["geo ref dataset"]["path"]
            == "https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSnBathymetryV17-02"
        )
        assert model_profile["geo ref dataset"]["y coord"] == "gridY"
        assert model_profile["geo ref dataset"]["x coord"] == "gridX"
        assert model_profile["extraction time origin"] == arrow.get("2007-01-01").date()
        assert (
            model_profile["results archive"]["path"]
            == "/results2/SalishSea/nowcast-green.201905/"
        )

    @pytest.mark.parametrize(
        "var_group, file_pattern, depth_coord",
        (
            (
                "auxiliary",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "biology",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc",
                "deptht",
            ),
            (
                "biology and chemistry rates",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_prod_T.nc",
                "deptht",
            ),
            (
                "chemistry",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "grazing and mortality",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_dia2_T.nc",
                "deptht",
            ),
            (
                "physics tracers",
                "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_T.nc",
                "deptht",
            ),
        ),
    )
    def test_SalishSeaCast_201905_day_datasets(
        self, var_group, file_pattern, depth_coord
    ):
        with (MODEL_PROFILES_DIR / "SalishSeaCast-201905.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)
        day_datasets = model_profile["results archive"]["datasets"]["day"]

        assert day_datasets[var_group]["file pattern"] == file_pattern
        assert day_datasets[var_group]["depth coord"] == depth_coord

    @pytest.mark.parametrize(
        "var_group, file_pattern, depth_coord",
        (
            (
                "auxiliary",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "biology",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc",
                "deptht",
            ),
            (
                "chemistry",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_carp_T.nc",
                "deptht",
            ),
            (
                "physics tracers",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_T.nc",
                "deptht",
            ),
            (
                "u velocity",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_U.nc",
                "depthu",
            ),
            (
                "v velocity",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_V.nc",
                "depthv",
            ),
            (
                "vertical turbulence",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
            (
                "w velocity",
                "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_W.nc",
                "depthw",
            ),
        ),
    )
    def test_SalishSeaCast_201905_hour_datasets(
        self, var_group, file_pattern, depth_coord
    ):
        with (MODEL_PROFILES_DIR / "SalishSeaCast-201905.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)
        hour_datasets = model_profile["results archive"]["datasets"]["hour"]

        assert hour_datasets[var_group]["file pattern"] == file_pattern
        assert hour_datasets[var_group]["depth coord"] == depth_coord


class TestHRDPS2_5kmOperational:
    """Test of contents of HRDPS-2.5km-operational model profile YAML."""

    def test_HRDPS2_5kmOperational_dataset(self):
        with (MODEL_PROFILES_DIR / "HRDPS-2.5km-operational.yaml").open("rt") as f:
            model_profile = yaml.safe_load(f)
        dataset_hour = model_profile["results archive"]["datasets"]["hour"]

        assert model_profile["name"] == "HRDPS-2.5km-operational"
        assert model_profile["time coord"]["name"] == "time_counter"
        assert model_profile["y coord"]["name"] == "y"
        assert model_profile["y coord"]["units"] == "metres"
        assert (
            model_profile["y coord"]["comment"]
            == "gridY values are distance in metres in the model y-direction from the south-west corner of the grid"
        )
        assert model_profile["x coord"]["name"] == "x"
        assert model_profile["x coord"]["units"] == "metres"
        assert (
            model_profile["x coord"]["comment"]
            == "gridX values are distance in metres in the model x-direction from the south-west corner of the grid"
        )
        expected_chunk_size = {
            "time": 24,
            "y": 266,
            "x": 256,
        }
        assert model_profile["chunk size"] == expected_chunk_size
        assert (
            model_profile["geo ref dataset"]["path"]
            == "https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSaAtmosphereGridV1"
        )
        assert model_profile["geo ref dataset"]["y coord"] == "gridY"
        assert model_profile["geo ref dataset"]["x coord"] == "gridX"
        assert model_profile["extraction time origin"] == arrow.get("2007-01-01").date()
        assert (
            model_profile["results archive"]["path"]
            == "/results/forcing/atmospheric/GEM2.5/operational/"
        )
        assert (
            dataset_hour["surface fields"]["file pattern"] == "ops_{nemo_yyyymmdd}.nc"
        )
        assert "depth coord" not in dataset_hour["surface fields"]


class TestHRDPS2_5kmGEMLAM_pre22sep11:
    """Test of contents of HRDPS-2.5km-GEMLAM-pre22sep11 model profile YAML."""

    def test_HRDPS2_5kmGEMLAM_pre22sep11_dataset(self):
        with (MODEL_PROFILES_DIR / "HRDPS-2.5km-GEMLAM-pre22sep11.yaml").open(
            "rt"
        ) as f:
            model_profile = yaml.safe_load(f)
        dataset_hour = model_profile["results archive"]["datasets"]["hour"]

        assert model_profile["name"] == "HRDPS-2.5km-GEMLAM-pre22sep11"
        assert model_profile["time coord"]["name"] == "time_counter"
        assert model_profile["y coord"]["name"] == "y"
        assert "units" not in model_profile["y coord"]
        assert "comment" not in model_profile["y coord"]
        assert model_profile["x coord"]["name"] == "x"
        assert "units" not in model_profile["x coord"]
        assert "comment" not in model_profile["x coord"]
        expected_chunk_size = {
            "time": 24,
            "y": 266,
            "x": 256,
        }
        assert model_profile["chunk size"] == expected_chunk_size
        assert (
            model_profile["geo ref dataset"]["path"]
            == "/results/forcing/atmospheric/GEM2.5/gemlam/gemlam_y2007m01d03.nc"
        )
        assert model_profile["geo ref dataset"]["y coord"] == "y"
        assert model_profile["geo ref dataset"]["longitude var"] == "nav_lon"
        assert model_profile["geo ref dataset"]["x coord"] == "x"
        assert model_profile["geo ref dataset"]["latitude var"] == "nav_lat"
        assert model_profile["extraction time origin"] == arrow.get("2007-01-01").date()
        assert (
            dataset_hour["surface fields"]["file pattern"]
            == "gemlam_{nemo_yyyymmdd}.nc"
        )
        assert "depth coord" not in dataset_hour["surface fields"]


class TestHRDPS2_5kmGEMLAM_22sep11onward:
    """Test of contents of HRDPS-2.5km-GEMLAM-22sep11onward model profile YAML."""

    def test_HRDPS2_5kmGEMLAM_22sep11onward_dataset(self):
        with (MODEL_PROFILES_DIR / "HRDPS-2.5km-GEMLAM-22sep11onward.yaml").open(
            "rt"
        ) as f:
            model_profile = yaml.safe_load(f)
        dataset_hour = model_profile["results archive"]["datasets"]["hour"]

        assert model_profile["name"] == "HRDPS-2.5km-GEMLAM-22sep11onward"
        assert model_profile["time coord"]["name"] == "time_counter"
        assert model_profile["y coord"]["name"] == "y"
        assert "units" not in model_profile["y coord"]
        assert "comment" not in model_profile["y coord"]
        assert model_profile["x coord"]["name"] == "x"
        assert "units" not in model_profile["x coord"]
        assert "comment" not in model_profile["x coord"]
        expected_chunk_size = {
            "time": 24,
            "y": 266,
            "x": 256,
        }
        assert model_profile["chunk size"] == expected_chunk_size
        assert (
            model_profile["geo ref dataset"]["path"]
            == "/results/forcing/atmospheric/GEM2.5/gemlam/gemlam_y2011m09d22.nc"
        )
        assert model_profile["geo ref dataset"]["y coord"] == "y"
        assert model_profile["geo ref dataset"]["longitude var"] == "nav_lon"
        assert model_profile["geo ref dataset"]["x coord"] == "x"
        assert model_profile["geo ref dataset"]["latitude var"] == "nav_lat"
        assert model_profile["extraction time origin"] == arrow.get("2007-01-01").date()
        assert (
            dataset_hour["surface fields"]["file pattern"]
            == "gemlam_{nemo_yyyymmdd}.nc"
        )
        assert "depth coord" not in dataset_hour["surface fields"]
