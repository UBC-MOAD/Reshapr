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
import pytest

from reshapr.api.v1 import extract


class TestExtractDataset:
    """Unit test for extract_dataset() function."""

    def test_extract_dataset(self):
        with pytest.raises(NotImplementedError):
            extract.extract_dataset()


class TestExtractNetcdf:
    """Unit test for extract_netcdf() function."""

    def test_extract_netcdf(self):
        with pytest.raises(NotImplementedError):
            extract.extract_netcdf()
