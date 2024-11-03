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

:command:`reshaper info --help` will show you how you can get other information to help you
use ``Reshapr``:

.. code-block:: text

    Usage: reshapr info [OPTIONS] [CLUSTER_OR_MODEL]

      Provide information about the installed Reshapr package.

      With no cluster or model profile the following information is shown:

      * versions of reshapr, xarray, dask & netcdf4 packages

      * list of dask cluster configurations included in the package

      * list of model profiles included in the package

      Specify a dask cluster configuration (e.g. `reshapr info salish_cluster`) or
      a model profile (e.g. `reshpr info SalishSeaCast-201905`) to get information
      about them.

    Options:
      --help  Show this message and exit.


:command:`info cluster`
=======================

:command:`reshaper info` followed by one of the dask cluster configurations shown in the
basic information list will show you the cluster settings.

Please see :ref:`ReshaprDaskClusterYAMLFile` for details about cluster configs.

Example:

.. code-block:: bash

    (reshapr)$ reshapr info salish_cluster.yaml

.. code-block:: text

    salish_cluster.yaml:
      # Configuration for a dask cluster on salish

      name: salish dask cluster
      processes: True
      number of workers: 4
      threads per worker: 1

    Please use reshapr info --help to learn how to get other information,
    or reshapr --help to learn about other sub-commands.


:command:`info model-profile`
=============================

:command:`reshaper info` followed by one of the model profiles shown in the
basic information list will show you information about model product time intervals
and variable groups.

Please see :ref:`ReshaprModelProfileYAMLFiles` for details about model profiles.

Example:

.. code-block:: bash

    (reshapr)$ reshapr info SalishSeaCast-201905.yaml

.. code-block:: text

    SalishSeaCast-201905.yaml:
    variable groups from time intervals in this model:
      day
        auxiliary
        biology
        biology and chemistry rates
        chemistry
        grazing and mortality
        physics tracers
      hour
        auxiliary
        biology
        chemistry
        physics tracers
        u velocity
        v velocity
        vertical turbulence
        w velocity

    Please use reshapr info model-profile time-interval variable-group
    (e.g. reshapr info SalishSeaCast-201905 hour biology)
    to get the list of variables in a variable group.

    Please use reshapr info --help to learn how to get other information,
    or reshapr --help to learn about other sub-commands.


:command:`info model-profile time-interval variable-group`
==========================================================

:command:`reshaper info model-profile` followed by one of the time intervals,
and one of the variable group names for that time interval
(shown in the model profile information output)
will show you the list of model variables available in the variable group for
that time interval.

Please see :ref:`ReshaprModelProfileYAMLFiles` for details about model profiles.

Example:

.. code-block:: bash

    (reshapr)$ reshapr info SalishSeaCast-201905.yaml hour biology

.. code-block:: text

    SalishSeaCast-201905.yaml:
    hour-averaged variables in biology group:
      - nitrate : Nitrate Concentration [mmol m-3]
      - ammonium : Ammonium Concentration [mmol m-3]
      - silicon : Silicon Concentration [mmol m-3]
      - diatoms : Diatoms Concentration [mmol m-3]
      - flagellates : Flagellates Concentration [mmol m-3]
      - ciliates : Mesodinium rubrum Concentration [mmol m-3]
      - microzooplankton : Microzooplankton Concentration [mmol m-3]
      - dissolved_organic_nitrogen : Dissolved Organic N Concentration [mmol m-3]
      - particulate_organic_nitrogen : Particulate Organic N Concentration [mmol m-3]
      - biogenic_silicon : Biogenic Silicon Concentration [mmol m-3]
      - mesozooplankton : Mesozooplankton Concentration [mmol m-3]

    Please use reshapr info --help to learn how to get other information,
    or reshapr --help to learn about other sub-commands.
