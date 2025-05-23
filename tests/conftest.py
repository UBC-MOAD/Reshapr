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


"""Fixtures for Reshapr test suite."""
import pytest
import structlog


@pytest.fixture(name="log_output")
def fixture_log_output():
    """Capture structlog log output for testing.

    Reference: https://www.structlog.org/en/stable/testing.html
    """
    return structlog.testing.LogCapture()


@pytest.fixture(autouse=True)
def fixture_configure_structlog(log_output):
    """Configure structlog log capture fixture.

    Reference: https://www.structlog.org/en/stable/testing.html
    """
    structlog.configure(processors=[log_output])
