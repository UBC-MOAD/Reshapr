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


"""Unit tests for command-line interface modules."""
import os
import textwrap

import structlog
from click.testing import CliRunner

import reshapr.cli.extract
from reshapr.cli import commands


class TestExtract:
    """Unit test for extract() CLI function."""

    def test_config_file_is_path(self, tmp_path):
        """re: GitHub issue #13: https://github.com/UBC-MOAD/Reshapr/issues/13

        Expect SystemExit exception due to model profile not found rather than AttributeError
        that occurred when click.Path() was not converting CLI arg to :py:class:`Path` instance.
        """
        config_yaml = tmp_path / "foo.yaml"
        config_yaml.write_text(
            textwrap.dedent(
                """\
                dataset:
                  model profile: bar
                """
            )
        )

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            start_date, end_date = "", ""
            result = runner.invoke(
                commands.reshapr,
                ["extract", os.fspath(config_yaml), start_date, end_date],
            )
        structlog.reset_defaults()

        assert result.exit_code == 2
        assert isinstance(result.exception, SystemExit)

    def test_start_end_dates_default_to_empty_string(self, tmp_path, monkeypatch):
        """re: GitHub issue #34: https://github.com/UBC-MOAD/Reshapr/issues/34

        Values from --start-date and --end-date CLI options should default to empty strings to
        prevent TypeError from arrow parser.
        """

        def mock_cli_extract(config_file, start_date, end_date):
            assert start_date == ""
            assert end_date == ""

        monkeypatch.setattr(
            reshapr.cli.extract.reshapr.core.extract, "cli_extract", mock_cli_extract
        )

        config_yaml = tmp_path / "foo.yaml"
        config_yaml.write_text(
            textwrap.dedent(
                """\
                dataset:
                  model profile: bar
                """
            )
        )

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                commands.reshapr, ["extract", os.fspath(config_yaml)]
            )
        structlog.reset_defaults()

        assert result.exit_code == 0
