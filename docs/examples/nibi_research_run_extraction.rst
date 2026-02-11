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
That strategy of "taking the compute to the data" is augmented by
the ability to run Jupyter and Marimo notebooks on the clusters via the VSCode Remove - SSH extension.

This section uses one of Jose's SHEM configuration collections of tuning runs for heterotrophic bacteria
as the research runs example.

Notable difference from other example uses include:

* The Reshapr model profile is maintained by the user doing the analysis rather than it being included
  in the Reshapr code repository.
  Please see the :ref:`SHEM-DayAvgModelProfile` section below for details.

* The extractions are run in interactive :command:`salloc` sessions
  or as jobs submitted via :command:`sbatch`


.. _SHEM-FileOrganizationAndExecutingExtractions:

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
Store your model profile YAML file in your analysis repository and commit it.
In the example above,
the file is :file:`analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml`.

You will also need to create an extraction configuration YAML file.
Please see the :ref:`SHEM-ExtractConfig` section below for details and an example file.
In the example above,
the file is :file:`analysis-doug/notebooks/SHEM/extract_SHEM_heterotrophic_bacteria.yaml`.
If you start from the example file below,
please be sure to edit it to set the correct paths for your system:

* line 5 that starts with ``model profile:`` to set the absolute path to your copy of the
  model profile YAML file
* line 18 that starts with ``dest dir:`` to set the absolute path to your directory where you will
  store the results of your extractions

Commit your modified extraction configuration YAML file.

Reshapr extractions *must* be run on compute nodes on ``nibi``,
not on the login nodes.
You can do this either in an interactive :command:`salloc` session
or as a batch job submitted via :command:`sbatch`.
Please see the :ref:`ReshaprBatchJobScript` section below for an example batch job script.

In a terminal session on ``nibi``,
request an interactive session with

.. code-block:: bash

    salloc --time=1:00:00 --mem-per-cpu=8000M --ntasks=16 --ntasks-per-node=16 --account=def-allen

* The values for ``--mem-per-cpu``,
  ``--ntasks``,
  and ``--ntasks-per-node`` are set to match the Dask cluster configuration in
  :file:`Reshapr/cluster_configs/nibi_cluster.yaml`.
* The values for ``--ntasks`` and ``--ntasks-per-node`` must be the same to ensure that
  all of the cores are allocated on the same node.
* Extractions typically take a few minutes each.
  So,
  a value for ``--time`` of tens of minutes to a few hours should be sufficient for most extractions.

Once your interactive session starts,
activate your ``reshapr`` conda environment and run your extraction with the
:command:`reshapr extract` command.
An example of doing that looks like:

.. code-block:: text

    cd $HOME/MEOPAR/analysis-doug/notebooks/SHEM/
    salloc --time=1:00:00 --mem-per-cpu=8000M --ntasks=16 --ntasks-per-node=16 --account=def-allen
    salloc: Pending job allocation 7615270
    salloc: job 7615270 queued and waiting for resources
    salloc: job 7615270 has been allocated resources
    salloc: Granted job allocation 7615270
    salloc: Waiting for resource configuration
    salloc: Nodes c205 are ready for job
    analysis-doug$ conda activate reshapr
    (/home/dlatorne/conda_envs/reshapr) analysis-doug$ reshapr extract extract_SHEM_heterotrophic_bacteria.yaml
    2026-01-26 14:43:35 [info     ] loaded config                  config_file=extract_SHEM_heterotrophic_bacteria.yaml
    2026-01-26 14:43:35 [info     ] loaded model profile           model_profile_yaml=/home/dlatorne/MEOPAR/analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml
    2026-01-26 14:43:40 [info     ] dask cluster dashboard         dashboard_link=http://127.0.0.1:8787/status dask_config_yaml=nibi_cluster.yaml
    2026-01-26 14:43:41 [info     ] extracting variables
    2026-01-26 14:44:48 [info     ] wrote netCDF4 file             nc_path=/scratch/dlatorne/test-reshapr/SHEM_day_tuning_pred_flag_heterotrophic_bacteria_20180226_20180701.nc
    2026-01-26 14:44:48 [info     ] total time                     t_total=67.281958341598511

Be sure to use the path
(relative or absolute) to your extraction YAML file in the :command:`reshapr extract` command.


.. _SHEM-DayAvgModelProfile:

SHEM Day-Averaged Results Model Profile
---------------------------------------

Here is an example model profile YAML file for Jose's SHEM tuning/pred_flag research run:

.. literalinclude:: Jose-SHEM-tuning-pred_flag.yaml
   :language: yaml
   :linenos:

The details of creating model profile YAML files are described in the
:ref:`ReshaprModelProfileYAMLFiles` section of the documentation.


Version Control Your Model Profile Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you create new model profile YAML files remember to give them descriptive names
and to commit them with messages that explain what they are for.
That ensures that your analysis progress will be well documented and reproducible.


.. _SHEM-ExtractConfig:

Extraction Configuration
------------------------

Here is an example extraction configuration YAML file for extracting heterotrophic bacteria
from Jose's SHEM tuning/pred_flag research run:

.. literalinclude:: extract_SHEM_heterotrophic_bacteria.yaml
   :language: yaml
   :linenos:


Start and/or End Dates
^^^^^^^^^^^^^^^^^^^^^^

You can change the start and/or end dates for the extraction by editing the ``start date:``
and/or ``end date:`` lines in the YAML file.
Alternatively,
you can use the ``--start-date`` and/or ``--end-date`` command-line options in the
:command:`reshapr extract` command to override the start and/or end dates in the YAML file.
Use :command:`reshapr extract --help` to see the details of how to do that.


Variables
^^^^^^^^^

You can change the variables that you extract by changing the ``variable group:`` name,
and the list of variables names in the lines following the ``extract variables:`` key in the YAML file.
To learn the names of the available variable groups and the variables in them,
use the :command:`reshapr info` command with the path and file name of your model profile.
For example:

.. code-block:: text

    reshapr info ~/MEOPAR/analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml
    /home/dlatorne/MEOPAR/analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml:
      Jose's SalishSeaCast v202111 NEMO SHEM config results stored on
      nibi. 26feb18-02jul18 tuning pred_flag run.

    variable groups from time intervals in this model:
      day
        biology
        biology growth rates
        grazing

    Please use reshapr info model-profile time-interval variable-group
    (e.g. reshapr info SalishSeaCast-201905 hour biology)
    to get the list of variables in a variable group.

    Please use reshapr info --help to learn how to get other information,
    or reshapr --help to learn about other sub-commands.

shows the list of day-averaged variable groups.
From that we can see the list of variables in the day-averaged biology variable group
with:

.. code-block:: text

    reshapr info ~/MEOPAR/analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml day biology
    /home/dlatorne/MEOPAR/analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml:
      Jose's SalishSeaCast v202111 NEMO SHEM config results stored on
      nibi. 26feb18-02jul18 tuning pred_flag run.

    day-averaged variables in biology group:
      - nitrate : Nitrate Concentration [mmol m-3]
      - ammonium : Ammonium Concentration [mmol m-3]
      - silicon : Silicon Concentration [mmol m-3]
      - diatoms : Diatoms Concentration [mmol m-3]
      - flagellates : Flagellates Concentration [mmol m-3]
      - microzooplankton : Microzooplankton Concentration [mmol m-3]
      - dissolved_organic_nitrogen : Dissolved Organic N Concentration [mmol m-3]
      - particulate_organic_nitrogen : Particulate Organic N Concentration [mmol m-3]
      - biogenic_silicon : Biogenic Silicon Concentration [mmol m-3]
      - mesozooplankton : Mesozooplankton Concentration [mmol m-3]
      - heterotrophic_bacteria : Heterotrophic Bacteria Concentration [mmol m-3]
      - dissolved_oxygen : Dissolved Oxygen Concentration [mmol m-3]
      - dissolved_inorganic_carbon : Dissolved Inorganic C Concentration [mmol m-3]
      - total_alkalinity : Total Alkalinity Concentration [mmol m-3]

    Please use reshapr info --help to learn how to get other information,
    or reshapr --help to learn about other sub-commands.


Depth-y-x Slab Selection
^^^^^^^^^^^^^^^^^^^^^^^^

You can specify depth,
y direction,
and x direction limits of your extraction by adding a ``selection:`` section to the YAML file
after the ``extracted dataset:`` section.
Example:

.. code-block:: yaml

    dataset:
      model profile: /home/dlatorne/MEOPAR/analysis-doug/notebooks/SHEM/model_profiles/Jose-SHEM-tuning-pred_flag.yaml
      time base: day
      variables group: biology

    dask cluster: nibi_cluster.yaml

    start date: 2018-02-26
    end date: 2018-07-02

    extract variables:
      - heterotrophic_bacteria

    selection:
      depth:
        # NOTE: use depth level numbers, not depths in meters
        depth min: 0
        depth max: 31
      grid y:
        y min: 450
        y max: 651
      grid x:
        x min: 200
        x max: 301

    extracted dataset:
      name: SHEM_day_tuning_pred_flag_heterotrophic_bacteria
      description: Daily heterotrophic bacteria extracted from SHEM tuning/pred_flag run;
                  depth levels=0:30, y=450:650, x=200:300
      dest dir: /scratch/dlatorne/test-reshapr/

Remember that Python uses 0-based indexing and that Python intervals are open on the right.
So,
to get the the y grid point from 430 to 470 you need to use:

.. code-block:: yaml

    selection:
      grid y:
        y min: 430
        y max: 471


Extraction File Name and Path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can change the beginning of the file name that your extracted netCDF dataset file will be
written to and the description in its metadata by editing the ``name:`` and ``description:`` values
in the ``extracted dataset:`` section of the YAML file.
The full file name will have the start and end dates appended to the ``name:`` value
in the format ``_YYYYMMDD_YYYYMMDD.nc``.
With ``SHEM_day_tuning_pred_flag_heterotrophic_bacteria`` as the value of ``name:``,
an extraction for 2018-02-26 to 2018-07-02 will produce a netCDF file called
:file:`SHEM_day_tuning_pred_flag_heterotrophic_bacteria_20180226_20180702.nc`.

You can change the directory where your extracted netCDF dataset files will be written to
by editing the ``dest dir:`` value in the ``extracted dataset:`` section of the YAML file.
As noted in :ref:`SHEM-FileOrganizationAndExecutingExtractions`,
*do not* store extracted netCDF dataset files in a Git repository or try to commit and push them
to GitHub - they are too large.


Version Control Your Extraction YAML Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As you build your collection of extraction YAML files remember to give them descriptive names
and to commit them with messages that explain what they are for.
That ensures that your analysis progress will be well documented and reproducible.


.. _ReshaprBatchJobScript:

Reshapr Batch Job Script Example
--------------------------------

As an alternative to running your extractions in interactive :command:`salloc` sessions,
you can run them as batch jobs submitted via :command:`sbatch`.
Here is an example batch job script for running an extraction:

.. literalinclude:: extract_nibi.sh
   :language: bash
   :linenos:

As in the interactive :command:`salloc` example above,

* The values for ``#SBATCH --mem-per-cpu``,
  ``#SBATCH --ntasks``,
  and ``#SBATCH --ntasks-per-node`` directives are set to match the Dask cluster configuration in
  :file:`Reshapr/cluster_configs/nibi_cluster.yaml`.
* The values for ``#SBATCH --ntasks`` and ``#SBATCH --ntasks-per-node`` must be the same to ensure
* that all of the cores are allocated on the same node.

Lines 16 and 17 in the script enable ``conda`` and activate the ``reshapr`` conda environment.

Submit the batch job with:

.. code-block:: bash

    sbatch extract_nibi.sh
