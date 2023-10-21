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


.. _IonaWastewaterDischargeAnalysis:

Analysis of NEMO Runs with Iona Wastewater Discharge
====================================================

Susan is running various configurations of version 202111 that include a simulation of the Iona
Island Wastewater Treatment Plant Deep Sea Outfall.
Since those are "research run results" in contrast to collections of daily results files from
long-running hindcasts the handling of the results files and the Reshapr model profile(s) is a little different.

.. note::
     This section serves as a guide for use of Reshapr for other "research run" applications.

Notable differences include:

* The research runs are executed on an HPC cluster in multi-day segments.
  For the Iona wastewater case the runs were done on ``graham``.
  Initial runs were 5 days long for debugging,
  tunning,
  and initial analysis development by Jake.
  Subsequent runs were 1 month long because that fits well in the 12-hour walltime scheduler
  partition on ``graham``.

* The run results are downloaded from the HPC cluster to research storage on :file:`/ocean/$USER/`
  or :file:`/data/$USER/`.
  For the Iona wastewater case the results were downloaded to directory trees in
  :file:`/data/sallen/results/MEOPAR/wastewater/` such as
  :file:`/data/sallen/results/MEOPAR/wastewater/long_run/`.

* The multi-day run results files like
  :file:`/data/sallen/results/MEOPAR/wastewater/long_run/SalishSea_1h_20180101_20180131_grid_T.nc`
  *must* be split into 1-day files stored in date-named subdirectories like
  :file:`/data/sallen/results/MEOPAR/wastewater/long_run/01jan18/SalishSea_1h_20180101_20180101_grid_T.nc`.
  At the moment,
  the beast way to do that is via the SalishSeaCast automation :py:mod:`nowcast.workers.split_results`
  worker.
  Only Doug and Susan have the necessary permissions to run that worker.
  Please ask them for help if you need to split results from another research run.

* The Reshapr model profile is maintained by the user doing the analysis rather than it being included
  in the Reshapr code repository.
  Please see the :ref:`IonaWastewaterModelProfile` section below for details.


File Organization and Executing Extractions
-------------------------------------------

Store your model profile and extraction configuration YAML files in a Git repository such as your
analysis repository so that you can commit your changes to them and push them to GitHub to document
your analysis history and make it reproducible.
Here is an example from :file:`analysis-doug`:

.. code-block:: text

    analysis-doug/
    ├── ...
    ├── notebooks
    │   ├── ...
    │   └── wastewater
    │       ├── extract_biology.yaml
    │       └── model_profiles
    │           └── SalishSeaCast-202111-wastewater-salish.yaml

Store the results of your extractions outside of a Git repository,
for example,
:file:`/ocean/dlatorne/MOAD/extractions/`.
Extracted netCDF files are large binary files.
*Do not try to push them to GitHub.*
If you commit them and push them to GitHub you will quickly exceed file and repository size limits.
They are products of the extraction process described by your model profile and extraction
configuration YAML files.
So,
having those YAML files under version control is sufficient to enable you to reproduce the
extracted netCDF files.

Grab a copy of the model profile YAML file that Doug created:
https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/wastewater/model_profiles/SalishSeaCast-202111-wastewater-salish.yaml
Store your copy of that file in your analysis repository and commit it.

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


Changing the Extraction Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here is the contents of the example :file:`extract_biology.yaml` file:

.. code-block:: yaml
   :linenos:

    # Reshapr configuration to extract day-averages of interesting biology variables
    # near Iona Island wastewater outfall

    dataset:
      model profile: /ocean/dlatorne/MEOPAR/analysis-doug/notebooks/wastewater/model_profiles/SalishSeaCast-202111-wastewater-salish.yaml
      time base: day
      variables group: biology

    dask cluster: salish_cluster.yaml

    start date: 2018-01-01
    end date: 2018-01-02
    extract variables:
      - ammonium
      - nitrate
      - diatoms

    selection:
      depth:
        # NOTE: use depth level numbers, not depths in meters
        depth max: 30
      grid y:
        y min: 430
        y max: 471
      grid x:
        x min: 280
        x max: 321

    extracted dataset:
      name: SalishSeaCast_wastewater_day_avg_biology
      description: Day-averaged ammonium, nitrate & diatoms extracted from SalishSeaCast v202111
                   NEMO model with wastewater outfalls
      dest dir: /ocean/dlatorne/MOAD/extractions/


You can change the start and/or end dates for the extraction by editing the ``start date:``
and/or ``end date:`` lines in the YAML file.
Alternatively,
you can use the ``--start-date`` and/or ``--end-date`` command-line options in the
:command:`reshapr extract` command to override the start and/or end dates in the YAML file.
Use :command:`reshapr extract --help` to see the details of how to do that.

You can change the variables that you extract by changing the ``variable group:`` name in line 5,
and the list of variables names in the lines following the ``extract variables:`` key at line 13.
To learn the names of the available variable groups and the variables in them,
use the :command:`reshapr info` command with the path and file name of your model profile.
For example:

.. code-block:: text

   reshapr info /ocean/dlatorne/MEOPAR/analysis-doug/notebooks/wastewater/model_profiles/SalishSeaCast-202111-wastewater-salish.yaml
   /ocean/dlatorne/MEOPAR/analysis-doug/notebooks/wastewater/model_profiles/SalishSeaCast-202111-wastewater-salish.yaml:
     SalishSeaCast version 202111 NEMO with wastewater outfalls results
     on storage accessible from salish.

   variable groups from time intervals in this model:
     day
       biology
       chemistry
       biology growth rates
       grazing
       light
       mortality
       physics tracers
       vvl grid
     hour
       biology
       chemistry
       light
       physics tracers
       turbulence
       u velocity
       v velocity
       vvl grid
       w velocity

   Please use reshapr info model-profile time-interval variable-group
   (e.g. reshapr info SalishSeaCast-201905 hour biology)
   to get the list of variables in a variable group.

   Please use reshapr info --help to learn how to get other information,
   or reshapr --help to learn about other sub-commands.

shows the lists of variable groups,
divided into day-averaged and hour-averaged collections.
From that we can see the list of variables in the day-averaged physics tracers variable group
with:

.. code-block:: text

    reshapr info SalishSeaCast-202111-salish.yaml day physics tracers
    SalishSeaCast-202111-salish.yaml:
      SalishSeaCast version 202111 NEMO results on storage accessible from
      salish. 2007-01-01 onward.

    day-averaged variables in physics tracers group:
      - sossheig : Sea Surface Height [m]
      - votemper : Conservative Temperature [degree_C]
      - vosaline : Reference Salinity [g kg-1]
      - sigma_theta : Potential Density (sigma_theta) [kg m-3]
      - e3t : T-cell Thickness [m]

    Please use reshapr info --help to learn how to get other information,
    or reshapr --help to learn about other sub-commands.

You can change the depth,
y direction,
and x direction limits of your extraction by editing the ``selection:`` section that starts on
line 18.
Remember that Python uses 0-based indexing and that Python intervals are open on the right.
So,
to get the the y grid point from 430 to 470 you need to use:

.. code-block:: yaml

    selection:
      grid y:
        y min: 430
        y max: 471

You can change the beginning of the file name that your extracted netCDF dataset will be written to
and the description in its metadata by editing the ``name:`` and ``description:`` values in lines
30 and 31.
With ``SalishSeaCast_wastewater_day_avg_biology`` as the value of ``name:``,
and extraction for 2018-01-01 to 2018-01-31 will produce a netCDF file called
:file:`SalishSeaCast_wastewater_day_avg_biology_20180101_20180131.nc`.

As you build your collection of extraction YAML files remember to give them descriptive names
and to commit them with messages that explain what they are for.
That ensures that your analysis progress will be well documented and reproducible.


.. _IonaWastewaterModelProfile:

Iona Wastewater Model Profile
-----------------------------

Coming soon.
