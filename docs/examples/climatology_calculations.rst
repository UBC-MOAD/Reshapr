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


.. _CalculationOfClimatologyDatasets:

Calculation of Climatology Datasets
===================================

Reshapr can be used to calculate climatology datasets from month or day averaged datasets.
Here is an example extraction configuration YAML file to calculate the monthly climatology of
a collection of physics variables extracted from SalishSeaCast v202111 hindcast.

.. literalinclude:: monthly_physics_climatology.yaml
   :language: yaml

The name of the time coordinate in the resulting dataset is ``month``;
i.e. the value of the ``group by:`` item in the ``climatology:`` stanza.
At present,
the only values accepted for ``group by:`` are ``month`` and ``day``,
and monthly climatology calculation has been much more thoroughly tested than daily.

A ``selection:`` stanza can be used in conjunction with ``climatology:`` to calculate a climatology
dataset for a subset of the model domain.

``climatology:`` and ``resample:`` are mutually exclusive.
An error message will be printed if you try to do an extraction with both in the configuration.
