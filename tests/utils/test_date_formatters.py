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


"""Tests for date formatter functions.
"""
import arrow
import pytest

from reshapr.utils import date_formatters


class Test_ddmmmyy:
    """Unit test for ddmmmyy() function."""

    def test_ddmmmyy(self):
        ddmmmyy = date_formatters.ddmmmyy(arrow.get("2022-02-07"))

        assert ddmmmyy == "07feb22"


class Test_yyyymmdd:
    """Unit test for yyyymmdd() function."""

    def test_yyyymmdd(self):
        yyyymmdd = date_formatters.yyyymmdd(arrow.get("2022-02-07"))

        assert yyyymmdd == "20220207"


class Test_yyyymm01:
    """Unit test for yyyymm01() function."""

    def test_yyyymm01(self):
        yyyymm01 = date_formatters.yyyymm01(arrow.get("2023-11-29"))

        assert yyyymm01 == "20231101"


@pytest.mark.parametrize(
    "day, expected",
    (
        ("2023-11-29", "20231130"),
        ("2023-11-01", "20231130"),
        ("2023-11-30", "20231130"),
        ("2023-02-15", "20230228"),
        ("2024-02-15", "20240229"),
    ),
)
class Test_yyyymm_end:
    """Unit test for yyyymm_end() function."""

    def test_yyyymm_end(self, day, expected):
        yyyymm_end = date_formatters.yyyymm_end(arrow.get(day))

        assert yyyymm_end == expected


class Test_yyyy:
    """Unit test for yyyy() function."""

    def test_yyyy(self):
        yyyy = date_formatters.yyyy(arrow.get("2022-08-31"))

        assert yyyy == "2022"


class Test_nemo_yyyymm:
    """Unit test for nemo_yyyymm() function."""

    def test_nemo_yyyymm(self):
        nemo_yyyymm = date_formatters.nemo_yyyymm(arrow.get("2022-08-08"))

        assert nemo_yyyymm == "y2022m08"


class Test_nemo_yyyymmdd:
    """Unit test for nemo_yyyymmdd() function."""

    def test_nemo_yyyymmdd(self):
        nemo_yyyymmdd = date_formatters.nemo_yyyymmdd(arrow.get("2022-02-28"))

        assert nemo_yyyymmdd == "y2022m02d28"
