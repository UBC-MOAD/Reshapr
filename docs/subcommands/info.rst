.. Copyright 2022 – present, UBC EOAS MOAD Group and The University of British Columbia
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    https://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.

.. SPDX-License-Identifier: Apache-2.0


***************************
:command:`info` Sub-command
***************************

The :command:`info` sub-command provides information about your installed version of ``Reshapr``
and the ``dask`` clusters and model profiles that are included with it.
Here is an example of the most basic level of output from :command:`reshapr info`:

.. code-block:: text

    reshapr, version 22.1.dev0
    xarray, version 0.21.1
    dask, version 2022.2.0
    netcdf4, version 1.5.8

    dask cluster configurations included in this package:
      salish_cluster.yaml

    model profiles included in this package:
      SalishSeaCast-201905.yaml
      SalishSeaCast-201812.yaml
      HRDPS-2.5km-GEMLAM-22sep11onward.yaml
      HRDPS-2.5km-GEMLAM-pre22sep11.yaml
      HRDPS-2.5km-operational.yaml

    Please use reshapr info --help to learn how to get deeper information,
    or reshapr --help to learn about other sub-commands.
