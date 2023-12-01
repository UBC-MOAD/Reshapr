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


"""Date formatter functions.
"""


def ddmmmyy(arrow_date):
    """Return an Arrow date as a string formatted as lower-cased `ddmmmyy`; e.g. 28feb22.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as lower-cased `ddmmmyy`.
    :rtype: str
    """
    return arrow_date.format("DDMMMYY").lower()


def yyyymmdd(arrow_date):
    """Return an Arrow date as a string of digits formatted as `yyyymmdd`; e.g. 20220228.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as `yyyymmdd` digits.
    :rtype: str
    """
    return arrow_date.format("YYYYMMDD")


def yyyymm01(arrow_date):
    """Return the first day of the month for an Arrow date as a string of digits
    formatted as `yyyymm01`; e.g. 20220201.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as `yyyymm01` digits.
    :rtype: str
    """
    return arrow_date.format("YYYYMM01")


def yyyymm_end(arrow_date):
    """Return the last day of the month for an Arrow date as a string of digits
    formatted as `yyyymmdd`; e.g. 20220228.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as `yyyymmdd` digits.
    :rtype: str
    """
    return arrow_date.shift(months=+1).replace(day=1).shift(days=-1).format("YYYYMMDD")


def yyyy(arrow_date):
    """Return an Arrow date as a string of digits formatted as `yyyy`; e.g. 2022.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as `yyyy` digits.
    :rtype: str
    """
    return arrow_date.format("YYYY")


def nemo_yyyymm(arrow_date):
    """Return an Arrow date as a string formatted using the NEMO forcing date convention;
    i.e. y2022m02.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as NEMO forcing date.
    :rtype: str
    """
    return arrow_date.format("[y]YYYY[m]MM")


def nemo_yyyymmdd(arrow_date):
    """Return an Arrow date as a string formatted using the NEMO forcing date convention;
    i.e. y2022m02d28.

    :param arrow_date: Date/time to format.
    :type arrow_date: :py:class:`arrow.arrow.Arrow`

    :return: Date formatted as NEMO forcing date.
    :rtype: str
    """
    return arrow_date.format("[y]YYYY[m]MM[d]DD")
