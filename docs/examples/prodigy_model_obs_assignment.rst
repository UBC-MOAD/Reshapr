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


.. _ModelProductsForGradCourseAssignment:

Model Products for Grad Course Assignment
=========================================

An extraction of model fields is required for an assignment about comparison of
model results and field observations in the 2021W2 edition of the EOAS PRODIGY
directed studies course.
The objective of the assignment is to look at the observations of the high salinity,
low temperature and high pCO2 event of late July/early August 2015 that is discussed in
[Evans_etal_2019]_ in comparison to fields from SalishSeaCast.

The parameters of the SalishSeaCast datasets to be provided to the students are:

* Variables: nitrate, temperature, and salinity
* Day-averaged and hour-averaged fields for 2015-07-25 through 2015-08-04
* The hour-averaged fields are every 3rd hours (8 hours per day) to keep the file sizes
  manageable on laptops.
* The spatial extent of the fields is limited to y-grid points from 600 northward,
  and depth points from the surface to level 25,
  again, to keep the files sizes manageable on laptops.

.. [Evans_etal_2019] Evans, Wiley, Katie Pocock, Alex Hare, Carrie Weekes, Burke Hales,
   Jennifer Jackson, Helen Gurney-Smith, Jeremy T. Mathis, Simone R. Alin,
   and Richard A. Feely.
   "Marine CO2 patterns in the northern Salish Sea."
   Frontiers in Marine Science 5 (2019): 536.
   https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2018.00536/full


Execution
---------

The task described above can be accomplished using :py:obj:`Reshapr` on the MOAD compute
server :kbd:`salish` with the commands:

.. code-block:: bash

    (reshapr)$ reshapr extract Reshapr/docs/examples/extract_evans_nitrate_day_avg.yaml
    (reshapr)$ reshapr extract Reshapr/docs/examples/extract_evans_physics_day_avg.yaml
    (reshapr)$ reshapr extract Reshapr/docs/examples/extract_evans_nitrate_hour_avg.yaml
    (reshapr)$ reshapr extract Reshapr/docs/examples/extract_evans_physics_hour_avg.yaml

where the 4 extraction processing configuration YAML files contain:


:file:`extract_evans_nitrate_day_avg.yaml`
******************************************

.. literalinclude:: extract_evans_nitrate_day_avg.yaml
   :language: yaml


:file:`extract_evans_physics_day_avg.yaml`
******************************************

.. literalinclude:: extract_evans_physics_day_avg.yaml
   :language: yaml


:file:`extract_evans_nitrate_hour_avg.yaml`
*******************************************

.. literalinclude:: extract_evans_nitrate_hour_avg.yaml
   :language: yaml


:file:`extract_evans_physics_hour_avg.yaml`
*******************************************

.. literalinclude:: extract_evans_physics_hour_avg.yaml
   :language: yaml


Please see :ref:`ReshaprExtractYAMLFile` for details of meanings and choices available
for the items in those YAML files.
