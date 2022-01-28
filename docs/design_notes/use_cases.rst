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


*********
Use Cases
*********

.. _DiatomsNudgingForAtlantisEcosystemModel:

Diatoms Nudging for Atlantis Ecosystem Model
============================================

A configuration of the Atlantis Ecosystem model for the Salish Sea is being run for
decades long time scales.
It is initialized and forced with seawater velocity,
temperature,
and salinity fields from the SalishSeaCast NEMO model 2007 to present hindcast.
The 15+ years of SalishSeaCast fields are used in a repeating cycle over the multiple
decades of the Atlantis run durations.

There is concern that the biomass of many functional groups in the Salish Sea
ecology that Atlantis calculates drifts over the duration of the run to values that
are not plausible.
A strategy to try to mitigate that drift is to periodically nudge one or more of the
functional groups at the base of the food web towards values obtained from outside
of the Atlantis calculations.
Specifically,
we want to use the diatoms fields calculated by the SMELT component of the
SalishSeaCast NEMO model as values with which to nudge the Atlantis diatoms calculations.

It was decided to use the day-averaged diatoms biomass fields calculated by the
SalishSeaCast hindcast.
To accomplish that,
we need to create one or more files containing day-averaged diatoms biomass,
and grid longitude and latitude fields from the thousands of 1-day biological tracers
files that are the output of the SalishSeaCast hindcast runs.
The coordinates of the file(s) for Atlantis are:

* time in days since 2007-01-01 12:30:00
* depth in metres of the midpoints of the SalishSeaCast model grid layers
* gridY: indices in the along-strait (y, north-ish) direction of the SalishSeaCast grid
* gridX: indices in the cross-strait (x, east-ish) direction of the SalishSeaCast grid

The variables in the file(s) are:

* diatoms: the (time, depth, gridY, gridX) field of mole concentration of diatoms
  expressed as nitrogen in seawater
* longitudes: the (gridY, girdX) field of longitude values of the model grid points
* latitudes: the (gridY, girdX) field of latitude values of the model grid points

The storage attributes of the file(s) are:

* netCDF-4 classic format because that is the format that tools in the Atlantis processing
  pipeline require
* gridY and gridX are stored as 32 bit integers,
  all other coordinates and variables are stored as 32 bit floats
* zlib compression *is not* used because it is not supported by the Atlantis toolchain
* the chunk size for diatoms is (1, 40, 898, 398);
  i.e. the full 3D field per day
* the chunk size for the coordinates and the other variables is their array sizes
