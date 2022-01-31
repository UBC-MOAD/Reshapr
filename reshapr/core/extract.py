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


"""Extract model variable time series from model products.
"""
import os
import sys
import time
from pathlib import Path

import arrow
import structlog
import yaml

logger = structlog.get_logger()


def extract(config_file):
    """Extract model variable time series from model products.

    :param config_file: File path and name of the YAML file to read processing configuration
                        dictionary from.
                        Please see :ref:`ReshaprExtractYAMLFile` for details.
    :type config_file: :py:class:`pathlib.Path`
    """
    t_start = time.time()
    with config_file.open() as f:
        config = yaml.safe_load(f)
    log = logger.bind(config_file=os.fspath(config_file))
    log.debug("read config")
    start_date = arrow.get(config["start date"])
    end_date = arrow.get(config["end date"])
    log = log.bind(
        start_date=start_date.format("YYYY-MM-DD"),
        end_date=end_date.format("YYYY-MM-DD"),
    )

    t_total = time.time() - t_start
    log = log.bind(t_total=t_total)
    log.info(f"total time: {t_total:.3f}s")


# This stanza facilitates running the extract sub-command in a Python debugger
if __name__ == "__main__":
    config_file = Path(sys.argv[1])
    extract(config_file)
