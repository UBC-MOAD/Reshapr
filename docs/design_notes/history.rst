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


*******
History
*******

Origins
=======

Many elements of Dask that are foundational in the design of :kbd:`Reshapr` are explored
in `this dask_expts notebook`_
(best viewed via nbviewer.org at `dask_expts.ipynb`_).
Those elements include:

* Dask’s task graph architecture
* details of its threads,
  processes,
  and cluster schedulers
* the role that chunking plays in conjunction with those things

.. _this dask_expts notebook: https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/dask_expts.ipynb
.. _dask_expts.ipynb: https://nbviewer.org/github/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/dask_expts.ipynb

The results of that exploration were applied to one of the research task needs that is
a motivator for :kbd:`Reshapr`:

* extraction of time series of diatoms biomass from the 2007 to present SalishSeaCast
  hindcast to be used to nudge the Atlantis ecosystem model

in `this atlantis_nudge_diatoms notebook`_
(best viewed via nbviewer.org at `atlantis_nudge_diatoms.ipynb`_).

.. _this atlantis_nudge_diatoms notebook: https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/atlantis_nudge_diatoms.ipynb
.. _atlantis_nudge_diatoms.ipynb: https://nbviewer.org/github/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/atlantis_nudge_diatoms.ipynb

Code from that notebook was extracted into a `Python module`_ with a minimal command-line
interface.
That module was the prototype for the :command:`reshapr extract` sub-command
and contributed to the conceptualization of several of the abstractions that are used in
:kbd:`Reshapr`.

.. _Python module: https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/atlantis_nudge_diatoms.py
