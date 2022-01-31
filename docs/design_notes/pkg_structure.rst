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


*****************
Package Structure
*****************

.. code-block:: text

    Reshapr/
    ├── docs
    │   ├── design_notes
    │   ├── _static
    │   ├── subcommands
    │   └── _templates
    ├── envs
    ├── .github
    │   └── workflows
    ├── reshapr
    │   ├── api
    │   ├── cli
    │   ├── core
    │   └── utils
    └── tests


Package Code Tree: :file:`reshapr/`
===================================

.. _ReshaprAPIDirectory:

:file:`reshapr/api/`
--------------------

Coming soon...


.. _ReshaprCLIDirectory:

:file:`reshapr/cli/`
--------------------

:file:`reshapr/cli/commands.py` contains the `Click commands group`_ into which sub-commands
must be registered,
and the :py:func:`reshapr.add_command` calls to register the sub-commands.

.. _Click commands group: https://click.palletsprojects.com/en/8.0.x/quickstart/#nesting-commands

It is also where configuration of the `structlog logging framework`_ happens.
All console output from the sub-commands is done via that logging.

.. _structlog logging framework: https://www.structlog.org/en/stable/index.html

The other modules in :file:`reshapr/cli/` contain the `Click`_ command-line interface
functions for each of the sub-commands;
e.g. :py:func:`reshapr.cli.extract.extract`.

.. _Click: https://click.palletsprojects.com


:file:`reshapr/core/`
---------------------

The modules in :file:`reshapr/core/` contain the implementation of the sub-commands;
e.g. :py:mod:`reshapr.core.extract`.

.. note::
    The functions in the :file:`reshapr/core/` modules are not intended to be called
    directly.
    They are accessed either via their command-line interface in
    :ref:`ReshaprCLIDirectory`,
    or via their API interface in :ref:`ReshaprAPIDirectory`.


:file:`reshapr/utils/`
----------------------

Coming soon...
