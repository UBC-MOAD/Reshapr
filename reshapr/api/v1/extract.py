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


"""v1 extraction API."""

from reshapr.core import extract


def extract_dataset():
    """Not implemented.

    :return: TBD
    """
    raise NotImplementedError


def extract_netcdf(config, config_yaml):
    """Extract model variable(s) time series from model product to a netCDF file.

    Recommended use is to load the config dict from a YAML file
    (optionally overriding extraction state/end dates) with
    :py:func:`~reshapr.api.v1.extract.load_extraction_config`,
    then call this function.

    :param dict config: Extraction processing configuration dictionary.

    :param config_yaml: File path and name of the YAML file that the extraction processing
                        configuration dictionary was read from.
                        Used in netCDF4 file history metadata.
    :type config_yaml: :py:class:`pathlib.Path`

    :return: File path and name that netCDF4 file was written to.
    :rtype: :py:class:`pathlib.Path`
    """
    return extract.api_extract_netcdf(config, config_yaml)


def load_extraction_config(config_yaml, start_date=None, end_date=None):
    """Read an extraction processing configuration YAML file and return a config dict.

    If start/end dates are provided, use them to override the values from the YAML file.
    :py:obj:`None` means do not override.

    :param config_yaml: File path and name of the YAML file to read the extraction processing
                        configuration dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_yaml: :py:class:`pathlib.Path`

    :param start_date: Start date for extraction. When provided,
                       this date overrides the start date in config file.
    :type start_date:  :py:class:`arrow.arrow.Arrow` or :py:obj:`None`

    :param end_date: End date for extraction. When provided,
                     this date overrides the end date in config file.
    :type end_date:  :py:class:`arrow.arrow.Arrow` or :py:obj:`None`

    :return: Extraction processing configuration dictionary.
    :rtype: dict

    :raises: :py:exc:`ValueError` if processing configuration YAML file cannot be opened.
    """
    return extract.load_config(config_yaml, start_date, end_date)
