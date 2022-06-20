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


.. _DaskClusters:

*****************
``dask`` Clusters
*****************

Intro - coming soon


.. _OnDemandCluster:

On-Demand Cluster - The Easy Way
================================

Coming soon...


.. _PersistentDaskCluster:

Persistent Cluster
==================

For applications where multiple :py:obj:`Reshapr` processes need to be run,
setting up and managing a persistent ``dask`` cluster that your processes connect to and use avoids
the overhead of starting up a cluster for each :py:obj:`Reshapr`  process.

An example of the kind of processing where this approach is used is running ``reshapr extract`` in
a ``bash`` loop to resample day-averaged datasets to get month-averaged datasets.
That is a post-processing step that is done as part of running a SalishSeaCast hindcast.
The cluster scheduler,
workers,
and ``bash`` loop are all run in separate terminals in a ``tmux`` session on ``salish``.
An ``ssh`` tunnel can be set up to connect a browser session to the cluster dashboard for
monitoring and analysis of the processing.

.. note::
     In contrast to the on-demand clusters that are created when you just run a ``reshapr extract``
     command,
     persistent clusters must be managed.
     If you create a persistent cluster,
     it is your responsibility to shut it down when you are finished with it.

     If you know that another group member is also using a persistent cluster,
     consider coordinating with them to use the same cluster instead of spinning up
     a new cluster.

Here is a step-by-step example of using a persistent cluster to run ``reshapr extract`` in
a ``bash`` loop to resample day-averaged datasets to get month-averaged datasets:

#. Create a new ``tmux`` session on ``salish``:

   .. code-block:: bash

        $ tmux new -s month-avg-201905

#. In the first ``tmux`` terminal,
   activate your ``reshapr`` conda environment and launch the :command:`dask-scheduler`:

   .. code-block:: bash

       $ conda activate reshapr
       (reshapr)$ dask-scheduler

   Use :kbd:`Control-b ,` to rename the ``tmux`` terminal to ``dask-scheduler``.

   Make the note of the IP address and port numbers for the scheduler and dashboard in the log
   output; e.g.

   .. code-block:: text

      2022-06-16 12:15:58 - distributed.scheduler - INFO - Scheduler at: tcp://142.103.36.12:8786
      2022-06-16 12:15:58 - distributed.scheduler - INFO - dashboard at:                    :8787

   8786 and 8787 are the default scheduler and dashboard port number,
   respectively,
   but you may see different port numbers if there are other clusters already running.

#. Start a second ``tmux`` terminal with :kbd:`Control-b c`,
   activate your ``reshapr`` conda environment and launch the first :command:`dask-worker`
   as a background process using the scheduler IP address and port number noted above:

   .. code-block:: bash

       $ conda activate reshapr
       (reshapr)$ dask-worker --nworkers=1 --nthreads=4 142.103.36.12:8786 &

   Use :kbd:`Control-b ,` to rename the ``tmux`` terminal to ``dask-workers``.

   Additional workers can be added to the cluster by repeating the same :command:`dask-worker`
   command.
   The log output in the ``dask-scheduler`` terminal
   (:kbd:`Control-b 0`)
   will show the workers joining the cluster.

#. Start a third ``tmux`` terminal with :kbd:`Control-b c` and activate your ``reshapr`` conda
   environment there too.
   This is the terminal in which you will run :command:`reshapr extract` commands.

   To run those commands on the persistent cluster,
   set the value of the ``dask cluster`` item in your :ref:`ReshaprExtractYAMLFile` to the
   scheduler IP address and port number noted above;
   e.g.

   .. code-block:: yaml

      dask cluster: 142.103.36.12:8786


#. **Optional:** To monitor the cluster in your browser on your laptop or workstation,
   start a terminal session there and set up an ``ssh`` tunnel to the scheduler's dashboard port:

   .. code-block:: bash

      $ ssh -L -N 8787:salish:8787 salish

   That command creates an ``ssh`` tunnel between port 8787 on your laptop/workstation and port 8787
   on ``salish``.
   You can use any number ≥1024 you want instead of 8787 as the local port number on your
   laptop/workstation.
   The number after ``:salish:`` has to be the scheduler's dashboard port number noted above.
   The command also assumes that you have an entry for ``salish`` in your :file:`~/.ssh/config`
   file.

   Open a new tab in the browser on your laptop/workstation and go to ``http://localhost:8787/``
   to see the cluster dashboard.
