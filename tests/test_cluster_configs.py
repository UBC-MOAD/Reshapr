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


"""Tests for package-supplied dask cluster configuration YAML files."""
from pathlib import Path

import pytest
import yaml

CLUSTER_CONFIGS_DIR = Path(__file__).parent.parent / "cluster_configs"
CLUSTER_CONFIGS = (Path("salish_cluster.yaml"), Path("unit_test_cluster.yaml"))


class TestClusterConfigs:
    """Tests of dask cluster config YAML files."""

    def test_cluster_configs_coverage(self):
        cluster_configs = set(
            CLUSTER_CONFIGS_DIR / cluster for cluster in CLUSTER_CONFIGS
        )
        assert set(CLUSTER_CONFIGS_DIR.glob("*.yaml")) == cluster_configs

    @pytest.mark.parametrize("cluster_config_yaml", CLUSTER_CONFIGS)
    def test_required_items(self, cluster_config_yaml):
        with (CLUSTER_CONFIGS_DIR / cluster_config_yaml).open("rt") as f:
            cluster_config = yaml.safe_load(f)

        assert cluster_config["name"] is not None
        assert cluster_config["processes"] is not None
        assert cluster_config["number of workers"] is not None
        assert cluster_config["threads per worker"] is not None
        assert cluster_config["memory limit"] is not None


class TestSalishCluster:
    """Test of contents of salish_cluster config YAML."""

    def test_salish_cluster(self):
        with (CLUSTER_CONFIGS_DIR / "salish_cluster.yaml").open("rt") as f:
            cluster_config = yaml.safe_load(f)

        assert cluster_config["name"] == "salish dask cluster"
        assert cluster_config["processes"] is True
        assert cluster_config["number of workers"] == 4
        assert cluster_config["threads per worker"] == 1
        assert cluster_config["memory limit"] == "auto"


class TestUnitTestCluster:
    """Test of contents of unit_test_cluster config YAML."""

    def test_unit_test_cluster(self):
        with (CLUSTER_CONFIGS_DIR / "unit_test_cluster.yaml").open("rt") as f:
            cluster_config = yaml.safe_load(f)

        assert cluster_config["name"] == "unit test dask cluster"
        assert cluster_config["processes"] is True
        assert cluster_config["number of workers"] == 1
        assert cluster_config["threads per worker"] == 1
        assert cluster_config["memory limit"] == "auto"
