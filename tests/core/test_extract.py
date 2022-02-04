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


"""Unit test for core.extract module.
"""
import os
import textwrap

import pytest

from reshapr.core import extract


class TestLoadConfig:
    """Unit tests for core.extract._load_config() function."""

    def test_load_config(self, log_output, tmp_path):
        extract_config = tmp_path / "extract_config.yaml"
        extract_config.write_text(
            textwrap.dedent(
                """\
                dask cluster: docs/subcommands/salish_cluster.yaml

                start date: 2007-01-01
                end date: 2007-01-10
                """
            )
        )

        config = extract._load_config(extract_config)

        assert config["dask cluster"] == "docs/subcommands/salish_cluster.yaml"

        assert log_output.entries[0]["log_level"] == "debug"
        assert log_output.entries[0]["config_file"] == os.fspath(extract_config)
        assert log_output.entries[0]["event"] == "loaded config"

    def test_no_config_file(self, log_output, tmp_path):
        nonexistent_config = tmp_path / "extract_config.yaml"

        with pytest.raises(SystemExit) as exc_info:
            extract._load_config(nonexistent_config)

        assert exc_info.value.code == 1
        assert log_output.entries[0]["log_level"] == "error"
        assert log_output.entries[0]["config_file"] == os.fspath(nonexistent_config)
        assert log_output.entries[0]["event"] == "config file not found"
