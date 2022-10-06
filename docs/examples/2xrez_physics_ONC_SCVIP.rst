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


.. _T&SAtONC-SoG-CentalNodeFromSSC-202111DblResExpt:

Temperature & Salinity Fields at ONC SoG Cental Node from SalishSeaCast.202111 Double Resolution Experiment
===========================================================================================================

A configuration of version 202111 of the SalishSeaCast NEMO model with doubled spatial resolution
was run for 2017 during the summer of 2021.
It was an experiment supported by :abbr:`UBC-ARC (UBC Advanced Research Computing)`.
Objectives of the experiment were:

* to learn what oceanographic insights might be gained by running the model at double resolution

* to learn about the HPC compute,
  storage,
  and operational requirements and challenges associated with running the model at double
  resolution

One of the analysis tasks we decided to do to evaluate the double resolution run was to compare the
calculated temperature and salinity values to observations collected at the
:abbr:`ONC (OCean Networks Canada)` :abbr:`SCVIP (Strait of Georgia Central Instrument Platform)`
node.
It was decided to extract a 5x5x5 cube of values approximately centred on the location of the node.

The analysis notebook that uses the results of this extraction is:

* nbviewer: https://nbviewer.org/github/SalishSeaCast/analysis-doug/blob/main/notebooks/2xrez-2017/DeepWaterRenewal.ipynb
* GitHub: https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/2xrez-2017/DeepWaterRenewal.ipynb


Execution
---------

The task described above can be accomplished using :py:obj:`Reshapr` on the MOAD compute
server :kbd:`salish` with the command:

.. code-block:: bash

    (reshapr)$ reshapr extract Reshapr/docs/examples/extract_ONC_SCVIP_physics_hour_avg.yaml

where :file:`Reshapr/docs/examples/extract_ONC_SCVIP_physics_hour_avg.yaml`
is an extraction processing configuration YAML file containing:

.. literalinclude:: extract_ONC_SCVIP_physics_hour_avg.yaml
   :language: yaml

Please see :ref:`ReshaprExtractYAMLFile` for details of meanings and choices available
for the items in the YAML file.
