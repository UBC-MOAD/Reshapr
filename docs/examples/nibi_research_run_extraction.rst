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


.. _nibiResearchRunExtraction:

Extractions from Research Runs on ``nibi``
==========================================

The new Alliance HPC clusters
(``nibi``,
``fir``,
``rorqual``,
and ``trillium``)
that came online in mid-2025
have improved interactive session functionality that make it more attractive to do
analysis work on the clusters instead of downloading results to ``salish`` for analysis.
That strategy of "tasking the compute to the data" is augmented by
the ability to run Jupyter and Marimo notebooks on the clusters via the VSCode Remove - SSH extension.

This section uses one of Jose's SHEM configuration collections of tuning runs for heterotrophic bacteria
as the research runs example.

Notable difference from other example uses include:

* The Reshapr model profile is maintained by the user doing the analysis rather than it being included
  in the Reshapr code repository.
  Please see the :ref:`SHEM-DayAvgModelProfile` section below for details.

* The extractions are run in interactive :command:`salloc` sessions
  or as jobs submitted via :command:`sbatch`


File Organization and Executing Extractions
-------------------------------------------

Store your model profile and extraction configuration YAML files in a Git repository such as your
analysis repository so that you can commit your changes to them and push them to GitHub to document
your analysis history and make it reproducible.
Here is an example from :file:`analysis-doug`:

.. code-block:: text

    analysis-doug/
    ├── ...
    ├── notebooks/
    │   ├── ...
    │   └── SHEM/
    │       ├── extract_SHEM_heterotrophic_bacteria.yaml
    │       └── model_profiles/
    │           └── Jose-SHEM-tuning-pred_flag.yaml

Store the results of your extractions outside of a Git repository.
The :file:`/scratch/` file system is a good choice,
for example,
:file:`/scratch/dlatorne/SHEM/`.
Extracted netCDF files are large binary files.
*Do not try to push them to GitHub.*
If you commit them and push them to GitHub you will quickly exceed file and repository size limits.
They are products of the extraction process described by your model profile and extraction
configuration YAML files.
So,
having those YAML files under version control is sufficient to enable you to reproduce the
extracted netCDF files.

You will need to create a model profile YAML file.
Please see the :ref:`SHEM-DayAvgModelProfile` section below for details and an example file.
Store your file in your analysis repository and commit it.
In the example above,
the file is :file:`analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml`.




Grab a copy of the sample extraction configuration YAML file that Doug created:
https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/wastewater/extract_biology.yaml
Store your copy of that file in your analysis repository.
Edit 2 lines of that file

* line 5 that starts with ``model profile:`` to set the absolute path to your copy of the
  model profile YAML file
* line 33 that starts with ``dest dir:`` to set the absolute path to your directory where you will
  store the results of your extractions

Commit your modified file.

In a terminal session on ``salish``,
activate your ``reshapr`` conda environment,
and do a test extraction.
For Doug,
that looks like:

.. code-block:: text

    cd /ocean/dlatorne/MEOPAR/analysis-doug/
    analysis-doug$ conda activate reshapr
    (/home/dlatorne/conda_envs/reshapr) analysis-doug$ reshapr extract notebooks/wastewater/extract_biology.yaml
    2023-10-19 12:13:43 [info     ] loaded config                  config_file=notebooks/wastewater/extract_biology.yaml
    2023-10-19 12:13:43 [info     ] loaded model profile           model_profile_yaml=/ocean/dlatorne/MEOPAR/analysis-doug/notebooks/wastewater/model_profiles/SalishSeaCast-202111-wastewater-salish.yaml
    2023-10-19 12:13:48 [info     ] dask cluster dashboard         dashboard_link=http://127.0.0.1:8787/status dask_config_yaml=/ocean/dlatorne/MOAD/Reshapr-10jul23/cluster_configs/salish_cluster.yaml
    2023-10-19 12:13:49 [info     ] extracting variables
    2023-10-19 12:13:49,882 - distributed.nanny - WARNING - Restarting worker
    2023-10-19 12:13:50 [info     ] wrote netCDF4 file             nc_path=/ocean/dlatorne/MOAD/extractions/SalishSeaCast_wastewater_day_avg_biology_20180101_20180102.nc
    2023-10-19 12:13:50 [info     ] total time                     t_total=7.281958341598511

Be sure to use the path
(relative or absolute) to your extraction YAML file in the :command:`reshapr extract` command.



.. _SHEM-DayAvgModelProfile:

SHEM Day-Averaged Results Model Profile
---------------------------------------

.. literalinclude:: Jose-SHEM-tuning-pred_flag.yaml
   :language: yaml
