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


.. _ReshaprModelProfileYAMLFiles:

*******************
Model Profile Files
*******************

Model profiles are YAML files stored in the :file:`Reshapr/model_profiles/` directory.
They describe the structure of the output files of the models that :py:obj:`Reshapr`
can operate on in relation to the features and assumptions built into the :py:obj:`Reshapr`
code.

Here is an example of a model profile file:

.. literalinclude:: ../model_profiles/SalishSeaCast-201812.yaml
   :language: yaml


File Structure
==============

Model profile files are nested collections of key-value pairs with the values often
being another collection of key-value pairs.
They map directly to a nested Python dictionary in the code.
Because of that mapping the key-value pairs are also referred to as items.

The sections below describe the model profile items and collections of items,
referred to as stanzas.
The descriptions include conventions used in the keys and values,
whether the items are required or option,
what the default values for optional items are,
etc.

The default values are generally those associated with the SalishSeaCast NEMO model datasets.


:py:attr:`name` Item (Required)
-------------------------------

The name of the model profile.

Example:

.. code-block:: yaml

   name: SalishSeaCast.201812


.. _TimeCoordStanza:

:py:attr:`time coord` Stanza (Required)
---------------------------------------

The name of the netCDF time coordinate in the model dataset.

Example:

.. code-block:: yaml

   time coord:
     name: time_counter


:py:attr:`y coord` Stanza  (Required)
-------------------------------------

A collection of items that define the
(required)
name of the netCDF y-direction coordinate in the model dataset,
and the
(optional)
:py:attr:`units` and :py:attr:`comment` metadata for the y-direction coordinate in datasets
produced by :py:obj:`Reshapr`.

Examples:

* A :py:attr:`y coord` stanza that uses default values for the :py:attr:`units`
  and :py:attr:`comment` metadata items:

  .. code-block:: yaml

     y coord:
       name: y

* A :py:attr:`y coord` stanza that provides values for the :py:attr:`units`
  and :py:attr:`comment` metadata items:

  .. code-block:: yaml

     y coord:
       name: y
       units: metres
       comment: gridY values are distance in metres in the model y-direction from the south-west corner of the grid

Stanza items:

:py:attr:`name` (Required)
   The name of the netCDF y-direction coordinate in the model dataset.

:py:attr:`units` (Optional)
   The value for the :py:attr:`units` item in the metadata of the y-direction coordinate
   in datasets produced by :py:obj:`Reshapr`.

   The default value when :py:attr:`units` is omitted is ``count``,
   the conventional unit for a grid index in netCDF files.

:py:attr:`comment`  (Optional)
   The value for the :py:attr:`comment` item in the metadata of the y-direction coordinate
   in datasets produced by :py:obj:`Reshapr`.

   The default value when :py:attr:`comment` is omitted is
   ``gridY values are grid indices in the model y-direction``.


:py:attr:`x coord` Stanza (Required)
------------------------------------

A collection of items that define the
(required)
name of the netCDF x-direction coordinate in the model dataset,
and the
(optional)
:py:attr:`units` and :py:attr:`comment` metadata for the x-direction coordinate in datasets
produced by :py:obj:`Reshapr`.

Examples:

* A :py:attr:`x coord` stanza that uses default values for the :py:attr:`units`
  and :py:attr:`comment` metadata items:

  .. code-block:: yaml

     x coord:
       name: x

* A :py:attr:`x coord` stanza that provides values for the :py:attr:`units`
  and :py:attr:`comment` metadata items:

  .. code-block:: yaml

     x coord:
       name: x
       units: metres
       comment: gridX values are distance in metres in the model x-direction from the south-west corner of the grid

Stanza items:

:py:attr:`name` (Required)
   The name of the netCDF x-direction coordinate in the model dataset.

:py:attr:`units`  (Optional)
   The value for the :py:attr:`units` item in the metadata of the x-direction coordinate
   in datasets produced by :py:obj:`Reshapr`.

   The default value when :py:attr:`units` is omitted is ``count``,
   the conventional unit for a grid index in netCDF files.

:py:attr:`comment`  (Optional)
   The value for the :py:attr:`comment` item in the metadata of the x-direction coordinate
   in datasets produced by :py:obj:`Reshapr`.

   The default value when :py:attr:`comment` is omitted is
   ``gridX values are grid indices in the model x-direction``.


:py:attr:`chunk size` Stanza (Required)
---------------------------------------

A collection of items that define the netCDF chunk size parameters for reading dataset files.

Chunk size plays an important and somewhat complicated role in the generation of the dask
task graph.
Please see the dask docs about `chunk size selection and orientation`,
and the more `detailed docs about chunks`_.

.. _chunk size selection and orientation: https://docs.dask.org/en/latest/array-best-practices.html#select-a-good-chunk-size
.. _detailed docs about chunks: https://docs.dask.org/en/latest/array-chunks.html

Examples:

* A :py:attr:`chunk size` stanza for a dataset that contains fields with a depth coordinate:

  .. code-block:: yaml

     chunk size:
       time: 1
       depth: 40
       y: 898
       x: 398

* A :py:attr:`chunk size` stanza for a dataset that contains surface fields with no depth
  coordinate:

  .. code-block:: yaml

     chunk size:
       time: 24
       y: 266
       x: 256

Stanza items:

:py:attr:`time`  (Required)
   The chunk size of the time coordinate in the model dataset.

:py:attr:`depth`  (Optional)
   The chunk size of the depth coordinate in the model dataset.

   This item is not required for datasets that contains surface fields
   with no depth coordinate.

:py:attr:`y`  (Required)
   The chunk size of the y-direction coordinate in the model dataset.

:py:attr:`x`  (Required)
   The chunk size of the x-direction coordinate in the model dataset.


:py:attr:`geo ref dataset` Stanza (Required)
--------------------------------------------

A collection of items that define the dataset that provides the geolocation
mapping between grid y/x indices and longitude/latitude values for the fields
in the dataset.

Examples:

* :py:attr:`geo ref dataset` stanza for a dataset whose geolocation data is available
  from an ERDDAP server dataset

  .. code-block:: yaml

     geo ref dataset:
       path: https://salishsea.eos.ubc.ca/erddap/griddap/ubcSSnBathymetryV17-02
       y coord: gridY
       x coord: gridX

* :py:attr:`geo ref dataset` stanza for a dataset whose geolocation data is available
  from a netCDF file.
  This example also shows how non-default names of the longitude/latitude variables
  in the geolocation dataset are handled.

  .. code-block:: yaml

     geo ref dataset:
       path: /results/forcing/atmospheric/GEM2.5/gemlam/gemlam_y2007m01d03.nc
       y coord: y
       longitude var: nav_lon
       x coord: x
       latitude var: nav_lat

Stanza items:

:py:attr:`path`  (Required)
   The ERDDAP server URL or file system path of the dataset that provides the
   geolocation mapping between grid y/x indices and longitude/latitude values.

:py:attr:`y coord`  (Required)
   The name of the netCDF y-direction coordinate in the geolocation dataset.

:py:attr:`longitude var`  (Optional)
   The name of the netCDF longitude variable in the geolocation dataset
   if it is something other than ``longitude``.

:py:attr:`x coord`  (Required)
   The name of the netCDF x-direction coordinate in the geolocation dataset.

:py:attr:`latitude var` (Optional)
   The name of the netCDF latitude variable in the geolocation dataset
   if it is something other than ``latitude``.


:py:attr:`extraction time origin` Item (Required)
-------------------------------------------------

The date to use as the netCDF time origin for datasets extracted from the model
dataset.
The value is used to calculate the netCDF ``units`` attribute of the time coordinate
in extracted datasets;
e.g. ``days since 2015-01-01 12:00:00``.
It is also used to calculate the ``time_origin`` and ``comment`` attributes of the
time coordinate.
The value of the ``time_origin`` attribute is the data and time parts of the ``units``
attribute;
e.g. ``2015-01-01 12:00:00``.
The value of the ``comment`` attribute is an explanation of the dataset's time
coordinate values;
e.g.

::

   time values are UTC at the centre of the intervals over which the
   calculated model results are averaged;
   e.g. the field average values for 8 February 2022 have
   a time value of 2022-02-08 12:00:00Z

The quanta
(``days``, ``hours``)
and the time components in the ``units``,
``time_origin``,
and ``comment`` attributes determined by the value of the ``time base`` item
in the :ref:`ReshaprExtractYAMLFile`.

Example:

.. code-block:: yaml

   extraction time origin: 2015-01-01


:py:attr:`results archive` Stanza (Required)
--------------------------------------------

A nested collection of items that describe the file system paths and file names
in which various groups of model variables are stored.
The depth coordinate for each of the variable groups is also specified here.

Example:

.. code-block:: yaml

   results archive:
      path: /results/SalishSea/nowcast-green.201812/
      datasets:
         day:
            biology:
               file pattern: "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_ptrc_T.nc"
               depth coord: deptht
            u velocity:
               file pattern: "{ddmmmyy}/SalishSea_1d_{yyyymmdd}_{yyyymmdd}_grid_U.nc"
               depth coord: depthu
         hour:
            physics tracers:
               file pattern: "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_T.nc"
               depth coord: deptht
            u velocity:
               file pattern: "{ddmmmyy}/SalishSea_1h_{yyyymmdd}_{yyyymmdd}_grid_U.nc"
               depth coord: depthu

Stanza items:

:py:attr:`path` (Required)
   The absolute file system path of the directory tree in which the model dataset
   files are stored.

:py:attr:`datasets` (Required)
   The sub-stanza key for the collections of time base
   (``day``, ``hour``)
   collections of model datasets.

:py:attr:`<time base>` (Required)
   The sub-stanza key for the time base groups of model dataset variable groups.
   *Must be either* ``day`` *or* ``hour``.
   The time base keys are used as the value for the ``time base`` item
   in the :ref:`ReshaprExtractYAMLFile` as part of the specifation of which dataset
   to extract variables from.

:py:attr:`<variables group>` (Required)
   The sub-stanza key(s) for the collections of model variables in particular
   dataset files.
   The variable group keys are used as the value for the ``variable group`` item
   in the :ref:`ReshaprExtractYAMLFile` as part of the specification of which dataset
   to extract variables from.

:py:attr:`file pattern` (Required)
   The dataset path/file pattern for the model variables in a group.
   The file patterns are relative to the model dataset :py:attr:`path`
   described above.
   Elements of the pattern in brace brackets;
   e.g. ``{yyyymmdd}`` are replaced by dates in the format indicated.
   For example,
   for the date ``2022-05-27`` these are some of the date format pattern elements
   and the resulting formatted date strings:

   * ``ddmmmyy``; e.g. ``27may22``
   * ``yyyymmdd``; e.g. ``20220527``
   * ``yyyy``; e.g. ``2022``
   * ``nemo_yyyymmdd``; e.g. ``y2022m05d27``
   * ``nemo_yyyymm``; e.g. ``y2022m05``

   The supported date format pattern elements are the names of the :ref:`DateFormatters`
   functions.

:py:attr:`depth coord` (Required for all but purely surface datasets)
   The name of the netCDF depth coordinate in the variables group dataset.

   For datasets that contain *only* surface fields
   (i.e. *none* of the variables have a depth coordinate)
   the :py:attr:`depth coord` item is omitted.

   Example:

   .. code-block:: yaml

      results archive:
        path: /results/forcing/atmospheric/GEM2.5/operational/
        datasets:
          hour:
            surface fields:
              file pattern: "ops_{nemo_yyyymmdd}.nc"

   The :py:attr:`depth coord` item is required for datasets that contain a mixture of
   surface and depth-varying variables.
