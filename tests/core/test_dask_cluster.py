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


"""Unit test for get_dask_client() function."""
import os
import textwrap
from pathlib import Path

import dask.distributed
import pytest

from reshapr.core.extract import get_dask_client


@pytest.mark.filterwarnings("ignore:There is no current event loop:DeprecationWarning")
class TestGetDaskClient:
    """Unit tests for get_dask_client() function."""

    def test_load_cluster_config_from_path(self, log_output, tmp_path):
        dask_config_yaml = tmp_path / "test_cluster.yaml"
        dask_config_yaml.write_text(
            textwrap.dedent(
                """\
                name: test dask cluster
                processes: True
                number of workers: 1
                threads per worker: 1
                """
            )
        )

        client = get_dask_client(dask_config_yaml)
        client.close()

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["dask_config_yaml"] == os.fspath(dask_config_yaml)
        assert log_output.entries[0]["event"] == "loaded dask cluster config"

    def test_load_cluster_config_from_cluster_configs_dir(self, log_output):
        dask_config_yaml = Path("unit_test_cluster.yaml")

        client = get_dask_client(dask_config_yaml)
        client.close()

        assert log_output.entries[0]["log_level"] == "debug"
        cluster_configs_path = Path(__file__).parent.parent.parent / "cluster_configs"
        assert log_output.entries[0]["dask_config_yaml"] == os.fspath(
            cluster_configs_path / dask_config_yaml
        )
        assert log_output.entries[0]["event"] == "loaded dask cluster config"

    def test_no_cluster_config_from_path(self, log_output, tmp_path):
        dask_config_yaml = tmp_path / "nonexistent.yaml"
        with pytest.raises(SystemExit) as exc_info:
            get_dask_client(dask_config_yaml)

        assert exc_info.value.code == 2
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["dask_config_yaml"] == os.fspath(dask_config_yaml)
        assert log_output.entries[0]["event"] == "dask cluster config file not found"

    def test_no_cluster_config_in_cluster_configs_dir(self, log_output, tmp_path):
        nonexistent_dask_config_yaml = Path("nonexistent.yaml")
        with pytest.raises(SystemExit) as exc_info:
            get_dask_client(nonexistent_dask_config_yaml)

        assert exc_info.value.code == 2
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["dask_config_yaml"] == os.fspath(
            nonexistent_dask_config_yaml
        )
        assert log_output.entries[0]["event"] == "dask cluster config file not found"

    def test_bad_host_port_spec(self, log_output):
        dask_config_yaml = "127.0.0.1"
        with pytest.raises(SystemExit) as exc_info:
            get_dask_client(dask_config_yaml)

        assert exc_info.value.code == 1
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["dask_config_yaml"] == dask_config_yaml
        assert (
            log_output.entries[0]["event"]
            == "unrecognized dask cluster config; expected YAML file path or host_ip:port"
        )

    @pytest.mark.parametrize(
        "dask_config_yaml",
        (
            "localhost:4343",
            "127.0.0.1:4343",
        ),
    )
    def test_no_cluster(self, dask_config_yaml, log_output, monkeypatch):
        class MockClient:
            def __init__(self, dask_config_yaml):
                raise OSError

        monkeypatch.setattr(dask.distributed, "Client", MockClient)

        with pytest.raises(SystemExit) as exc_info:
            get_dask_client(dask_config_yaml)

        assert exc_info.value.code == 1
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["dask_config_yaml"] == dask_config_yaml
        assert (
            log_output.entries[0]["event"]
            == "requested dask cluster is not running or refused your connection"
        )

    def test_connect_to_cluster(self, log_output, tmp_path):
        cluster = dask.distributed.LocalCluster(
            name="test dask cluster",
            n_workers=1,
            threads_per_worker=1,
            processes=True,
        )
        dask_config_yaml = cluster.scheduler_address

        client = get_dask_client(dask_config_yaml)
        dashboard_link = client.dashboard_link
        client.close()

        assert log_output.entries[0]["log_level"] == "info"
        assert log_output.entries[0]["dask_config_yaml"] == dask_config_yaml
        assert log_output.entries[0]["dashboard_link"] == dashboard_link
        assert log_output.entries[0]["event"] == "dask cluster dashboard"

    def test_launch_cluster(self, log_output, tmp_path):
        dask_config_yaml = Path("unit_test_cluster.yaml")

        client = get_dask_client(dask_config_yaml)
        dashboard_link = client.dashboard_link
        client.close()

        assert log_output.entries[1]["log_level"] == "info"
        cluster_configs_path = Path(__file__).parent.parent.parent / "cluster_configs"
        assert log_output.entries[0]["dask_config_yaml"] == os.fspath(
            cluster_configs_path / dask_config_yaml
        )
        assert log_output.entries[1]["dashboard_link"] == dashboard_link
        assert log_output.entries[1]["event"] == "dask cluster dashboard"
