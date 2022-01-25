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


.. _ReshaprPackagedDevelopment:

**********************************************************
:kbd:`Reshapr` Package Development
**********************************************************


.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0
.. image:: https://img.shields.io/badge/python-3.10+-blue.svg
    :target: https://docs.python.org/3.10/
    :alt: Python Version
.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr
    :alt: Git on GitHub
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter
.. image:: https://readthedocs.org/projects/Reshapr/badge/?version=latest
    :target: https://reshapr.readthedocs.io/en/latest/
    :alt: Documentation Status
.. image:: https://img.shields.io/github/issues/UBC-MOAD/Reshapr?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr/issues
    :alt: Issue Tracker

The Reshapr package (:kbd:`Reshapr`) is Command-line tool based on Xarray and Dask
for extraction of model variable time series from model products like
SalishSeaCast, HRDPS & CANESM2/CGCM4.


.. _ReshaprPythonVersions:

Python Versions
===============

.. image:: https://img.shields.io/badge/python-3.10+-blue.svg
    :target: https://docs.python.org/3.10/
    :alt: Python Version

The :kbd:`Reshapr` package is developed and tested using `Python`_ 3.10.
The package uses some Python language features that are not available in various earlier versions,
in particular:

* `formatted string literals`_
  (aka *f-strings*)
  with :kbd:`=` specifiers

* `structural pattern matching`_

.. _Python: https://www.python.org/
.. _formatted string literals: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
.. _structural pattern matching: https://www.python.org/dev/peps/pep-0636/

.. _ReshaprGettingTheCode:

Getting the Code
================

.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr
    :alt: Git on GitHub

Clone the code and documentation `repository`_ from GitHub with:

.. _repository: https://github.com/UBC-MOAD/Reshapr

.. code-block:: bash

    $ git clone git@github.com:UBC-MOAD/Reshapr.git

or copy the URI
(the stuff after :kbd:`git clone` above)
from the :guilabel:`Code` button on the `repository`_ page.

.. note::

    The :kbd:`git clone` command above assumes that your are `connecting to GitHub using SSH`_.
    If it fails,
    please follow the instructions in our :ref:`moaddocs:SecureRemoteAccess` docs to
    set up your SSH keys and :ref:`moaddocs:CopyYourPublicSshKeyToGitHub`.

    .. _connecting to GitHub using SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh


.. _ReshaprDevelopmentEnvironment:

Development Environment
=======================

Setting up an isolated development environment using `Conda`_ is recommended.
Assuming that you have `Miniconda3`_ installed,
you can create and activate an environment called :kbd:`reshapr-dev` that will have
all of the Python packages necessary for development,
testing,
and building the documentation with the commands below.

.. _Conda: https://conda.io/en/latest/
.. _Miniconda3: https://docs.conda.io/en/latest/miniconda.html

.. code-block:: bash

    $ cd Reshapr
    $ conda env create -f envs/environment-dev.yaml
    $ conda activate reshapr
    (reshapr-dev)$ python3 -m pip install --editable .

The :kbd:`--editable` option in the :command:`pip install` command above installs
the package from the cloned repo via symlinks so that the installed package will be
automatically updated as the repo evolves.

To deactivate the environment use:

.. code-block:: bash

    (reshapr-dev)$ conda deactivate


.. _ReshaprCodingStyle:

Coding Style
============

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter

The :kbd:`Reshapr` package uses the `black`_ code formatting tool to maintain a
coding style that is very close to `PEP 8`_.

.. _black: https://black.readthedocs.io/en/stable/
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/

:command:`black` is installed as part of the :ref:`ReshaprDevelopmentEnvironment` setup.

To run :command:`black` on the entire code-base use:

.. code-block:: bash

    $ cd Reshapr
    $ conda activate reshapr
    (reshapr-dev)$ black ./

in the repository root directory.
The output looks something like:

.. code-block:: text

    **add example black output**


.. _ReshaprBuildingTheDocumentation:

Building the Documentation
==========================

.. image:: https://readthedocs.org/projects/reshapr/badge/?version=latest
    :target: https://reshapr.readthedocs.io/en/latest/
    :alt: Documentation Status

The documentation for the :kbd:`Reshapr` package is written in `reStructuredText`_
and converted to HTML using `Sphinx`_.
Creating a :ref:`ReshaprDevelopmentEnvironment` as described above includes the installation of Sphinx.
Building the documentation is driven by the :file:`docs/Makefile`.
With your :kbd:`reshapr-dev` development environment activated,
use:

.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/

.. code-block:: bash

    (reshapr-dev)$ (cd docs && make clean html)

to do a clean build of the documentation.
The output looks something like:

.. code-block:: text

    **add example Sphinx output**

The HTML rendering of the docs ends up in :file:`docs/_build/html/`.
You can open the :file:`index.html` file in that directory tree in your browser
to preview the results of the build.

If you have write access to the `repository`_ on GitHub,
whenever you push changes to GitHub the documentation is automatically re-built
and rendered at https://reshapr.readthedocs.io/en/latest/.


.. _ReshaprLinkCheckingTheDocumentation:

Link Checking the Documentation
-------------------------------

Sphinx also provides a link checker utility which can be run to find
broken or redirected links in the docs.
With your :kbd:`reshapr-dev)` environment activated,
use:

.. code-block:: bash

    (reshapr-dev))$ cd Reshapr/docs/
    (reshapr-dev)) docs$ make linkcheck

The output looks something like:

.. code-block:: text

    **add example linkcheck output**

Look for any errors in the above output or in _build/linkcheck/output.txt


.. _ReshaprRunningTheUnitTests:

Running the Unit Tests
======================

The test suite for the :kbd:`Reshapr` package is in :file:`Reshapr/tests/`.
The `pytest`_ tool is used for test parametrization and as the test runner for the suite.

.. _pytest: https://docs.pytest.org/en/latest/

With your :kbd:`reshapr-dev` development environment activated,
use:

.. code-block:: bash

    (reshapr-dev)$ cd Reshapr/
    (reshapr-dev)$ pytest

to run the test suite.
The output looks something like:

.. code-block:: text

    **add example pytest output**

You can monitor what lines of code the test suite exercises using the `coverage.py`_
and `pytest-cov`_ tools with the command:

.. _coverage.py: https://coverage.readthedocs.io/en/latest/
.. _pytest-cov: https://pytest-cov.readthedocs.io/en/latest/

.. code-block:: bash

    (reshapr-dev)$ cd Reshapr/
    (reshapr-dev)$ pytest --cov=./

and generate a test coverage report with:

.. code-block:: bash

    (reshapr-dev)$ coverage report

to produce a plain text report,
or

.. code-block:: bash

    (reshapr-dev)$ coverage html

to produce an HTML report that you can view in your browser by opening :file:`Reshapr/htmlcov/index.html`.


.. _ReshaprVersionControlRepository:

Version Control Repository
==========================

.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr
    :alt: Git on GitHub

The :kbd:`Reshapr` package code and documentation source files are available
as a `Git`_ repository at https://github.com/UBC-MOAD/Reshapr.

.. _Git: https://git-scm.com/


.. _ReshaprIssueTracker:

Issue Tracker
=============

.. image:: https://img.shields.io/github/issues/MIDOSS/WWatch3-Cmd?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr/issues
    :alt: Issue Tracker

Development tasks,
bug reports,
and enhancement ideas are recorded and managed in the issue tracker at
https://github.com/UBC-MOAD/Reshapr/issues.


License
=======

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0

The code and documentation of the Reshapr project
are copyright 2022 – present by the UBC EOAS MOAD Group and The University of British Columbia.

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
