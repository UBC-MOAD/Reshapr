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


**********
Motivation
**********

This is lightly edited version of a blurb written in December 2021 to provide background
for a contract from the Institute of Ocean Sciences (IOS) of the Fisheries and Oceans Canada (DFO)
that supported part of the development of :kbd:`Reshapr`.

Output from ocean and climate models is generally stored in NetCDF-4 files.
While atmospheric models often store results in GRIB2 files,
those files can be transformed into NetCDF-4 or processed via software libraries
in the same way as we will describe below.
Time series of one or more variables from such model results are a very common starting point
for analysis of model results,
evaluation of model skill in comparison to observations,
and generation of model products such as climatology.
Two general challenges to creating such time series are:

1) The variable values for the time period of interest are stored across many files;
   daily-ish in the case of operational models,
   perhaps monthly-ish in the case of climate hindcasts or forecasts for reasons of run
   and/or storage management

2) The files are often large;
   1 day of hour-averaged tracer variables from SalishSeaCast
   (24 hours, 40 depths levels, 398 x 898 x-y grid point) is 2.1 Gb on disk.
   That grows to about 10 Gb when the file is loaded into memory because SalishSeaCast,
   like many models, uses the on-the-fly compression feature of NetCDF-4 to reduce the
   on-disk size of its results by a factor of ~5.

Those challenges make the process of extracting a model variable time series
one of dealing with multiple files that exceed the available RAM if they are all loaded at once,
and that have a computational cost to simply open due to the necessary data decompression
operation.

The `Pangeo`_ community have `converged on`_ Python and the
`Xarray`_ and `Dask`_ packages to address those challenges.
Xarray provides a high level programming interface for labelled multi-dimensional arrays
that maps especially well to handling NetCDF-4 model results.
Dask provides a flexible parallel computing framework for operating on extremely large
datasets without loading them into memory.

.. _converged on: https://pangeo.io/packages.html#why-xarray-and-dask
.. _Pangeo: https://pangeo.io
.. _Xarray: https://xarray.pydata.org/en/latest/
.. _Dask: https://docs.dask.org/en/latest/

Sadly,
Xarray and Dask are not a panacea.
The :py:func:`xarray.open_mfdataset` function does an excellent job of abstracting away
the challenge of operating on tens or hundreds of multi-gigabyte files.
It also hides the added complication of the above-mentioned factor of ~5 expansion of
the in-memory size of the data compared to the file sizes.
Inexperienced researchers,
especially students,
are often confused and disappointed when it is,
at best,
slow,
or,
at worst,
fails due to exhausting the physical and virtual memory of the machine they are using.
Few researchers have the patience or computing background to delve into the nuances of
Dask’s task graph architecture,
the details of its threads,
processes,
and cluster schedulers,
and the role that chunking plays in conjunction with those things.

Doug Latornell has worked with Xarray and Dask for over 4 years and has explored
the performance space of Dask schedulers and chunking for a variety of operations
on the SalishSeaCast and HRPDS datasets.
He has used Xarray and Dask in the context of the SalishSeaCast modelling system,
and has advised researchers in the MOAD group and other groups at UBC and elsewhere on
their use.
That experience has led to the realization that there are a collection of basic operations,
such as extracting model variable time series,
that could be beneficially implemented in a Python package that codifies his experience
and the best practices he has learned.

That lead to the beginnings of the design of the :kbd:`Reshapr` package.
The immediate goal was to provide a command-line tool that is capable of extracting
time series of one or more model variables from the model results files that are used
in the SalishSeaCast project.
The implementation will take advantage of knowledge of the way the various model results
are stored,
and the machines that we work on to use Xarray and Dask optimally.
The code and documentation should facilitate optimal choices of Dask scheduler and chunking,
perhaps making automatic choices for different machines:
MOAD workstations,
the :kbd:`salish` compute server,
or Compute Canada HPC clusters.

Longer term goals include a Python API in addition to a command-line interface,
and more complex analysis operations such as temporal and spatial resampling,
and climatology calculations.

Apart from the codification of experience and knowledge, :kbd:`Reshapr` is motivated by
research task needs like:

* extraction of time series of diatoms biomass from the 2007 to present SalishSeaCast
  hindcast to be used to nudge the Atlantis ecosystem model
  (:ref:`DiatomsNudgingForAtlantisEcosystemModel`)

* extraction of time series of variables from SalishSeaCast models for cluster analysis
  to inform the partitioning of the Salish Sea in to similar regions for various research
  questions

* extraction of time series of variables from the Environment and Climate Change Canada
  (ECCC) High Resolution Deterministic Prediction System (HRDPS) atmospheric forecast
  model

As `open-source code on GitHub`_,
:kbd:`Reshapr` is available for use by DFO researchers and others,
to provide implementation guidance for other applications of Xarray and Dask.
It is able to accept contributions of knowledge about operating on other model datasets
of interest,
and other computing platforms.

.. _open-source code on GitHub: https://github.com/UBC-MOAD/Reshapr
