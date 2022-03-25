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

*************************************
:py:obj:`Reshapr` Package Development
*************************************


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
.. image:: https://github.com/UBC-MOAD/Reshapr/workflows/CI/badge.svg
    :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow%3ACI
    :alt: pytest and test coverage analysis
.. image:: https://codecov.io/gh/UBC-MOAD/Reshapr/branch/main/graph/badge.svg
    :target: https://app.codecov.io/gh/UBC-MOAD/Reshapr
    :alt: Codecov Testing Coverage Report
.. image:: https://github.com/UBC-MOAD/Reshapr/actions/workflows/codeql-analysis.yaml/badge.svg
    :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:CodeQL
    :alt: CodeQL analysis
.. image:: https://img.shields.io/github/issues/UBC-MOAD/Reshapr?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr/issues
    :alt: Issue Tracker

The Reshapr package (:py:obj:`Reshapr`) is Command-line tool based on Xarray and Dask
for extraction of model variable time series from model products like
SalishSeaCast, HRDPS & CANESM2/CGCM4.


.. _ReshaprPythonVersions:

Python Versions
===============

.. image:: https://img.shields.io/badge/python-3.10+-blue.svg
    :target: https://docs.python.org/3.10/
    :alt: Python Version

The :py:obj:`Reshapr` package is developed and tested using `Python`_ 3.10.
The package uses some Python language features that are not available in various earlier versions,
in particular:

* `formatted string literals`_
  (aka *f-strings*)
  with :kbd:`=` specifiers

* `structural pattern matching`_

.. _Python: https://www.python.org/
.. _formatted string literals: https://docs.python.org/3/reference/lexical_analysis.html#f-strings
.. _structural pattern matching: https://peps.python.org/pep-0636/

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

The :py:obj:`Reshapr` package uses the `black`_ code formatting tool to maintain a
coding style that is very close to `PEP 8`_.

.. _black: https://black.readthedocs.io/en/stable/
.. _PEP 8: https://peps.python.org/pep-0008/

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

The documentation for the :py:obj:`Reshapr` package is written in `reStructuredText`_
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

    Removing everything under '_build'...
    Running Sphinx v4.4.0
    making output directory... done
    loading intersphinx inventory from https://ubc-moad-docs.readthedocs.io/en/latest/objects.inv...
    loading intersphinx inventory from http://xarray.pydata.org/en/latest/objects.inv...
    intersphinx inventory has moved: http://xarray.pydata.org/en/latest/objects.inv -> https://xarray.pydata.org/en/latest/objects.inv
    building [mo]: targets for 0 po files that are out of date
    building [html]: targets for 4 source files that are out of date
    updating environment: [new config] 4 added, 0 changed, 0 removed
    reading sources... [100%] pkg_development
    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    preparing documents... done
    writing output... [100%] pkg_development
    generating indices... genindex done
    writing additional pages... search done
    copying static files... done
    copying extra files... done
    dumping search index in English (code: en)... done
    dumping object inventory... done
    build succeeded.

    The HTML pages are in _build/html.

The HTML rendering of the docs ends up in :file:`docs/_build/html/`.
You can open the :file:`index.html` file in that directory tree in your browser
to preview the results of the build.
If you use Firefox,
you can probably accomplish that with:

.. code-block:: bash

    (reshapr-dev)$ firefox docs/_build/html/index.html

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

    Running Sphinx v4.4.0
    making output directory... done
    loading pickled environment... done
    building [mo]: targets for 0 po files that are out of date
    building [linkcheck]: targets for 4 source files that are out of date
    updating environment: 0 added, 1 changed, 0 removed
    reading sources... [100%] pkg_development
    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    preparing documents... done
    writing output... [100%] pkg_development

    ( pkg_development: line   22) ok        https://black.readthedocs.io/en/stable/
    ( pkg_development: line  286) ok        https://coverage.readthedocs.io/en/latest/
    ( pkg_development: line  266) ok        https://docs.pytest.org/en/latest/
    (design_notes/motivation: line   53) ok        https://docs.dask.org/en/latest/
    ( pkg_development: line   22) ok        https://docs.python.org/3.10/
    ( pkg_development: line   62) ok        https://docs.python.org/3/reference/lexical_analysis.html#f-strings
    ( pkg_development: line  322) ok        https://git-scm.com/
    ( pkg_development: line  108) ok        https://docs.conda.io/en/latest/miniconda.html
    ( pkg_development: line  108) ok        https://conda.io/en/latest/
    ( pkg_development: line   22) ok        https://img.shields.io/badge/code%20style-black-000000.svg
    (           index: line   40) ok        https://img.shields.io/badge/license-Apache%202-cb2533.svg
    ( pkg_development: line   22) ok        https://img.shields.io/badge/python-3.10+-blue.svg
    ( pkg_development: line   22) ok        https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    ( pkg_development: line   95) ok        https://docs.github.com/en/authentication/connecting-to-github-with-ssh
    ( pkg_development: line   22) ok        https://img.shields.io/github/issues/UBC-MOAD/Reshapr?logo=github
    (design_notes/motivation: line   53) ok        https://pangeo.io
    (design_notes/motivation: line   53) ok        https://pangeo.io/packages.html#why-xarray-and-dask
    ( pkg_development: line  286) ok        https://pytest-cov.readthedocs.io/en/latest/
    ( pkg_development: line  331) ok        https://img.shields.io/github/issues/MIDOSS/WWatch3-Cmd?logo=github
    ( pkg_development: line   22) ok        https://reshapr.readthedocs.io/en/latest/
    ( pkg_development: line   95) ok        https://ubc-moad-docs.readthedocs.io/en/latest/ssh_access.html#copyyourpublicsshkeytogithub
    ( pkg_development: line   95) ok        https://ubc-moad-docs.readthedocs.io/en/latest/ssh_access.html#secureremoteaccess
    (           index: line   40) ok        https://www.apache.org/licenses/LICENSE-2.0
    ( pkg_development: line   22) ok        https://github.com/UBC-MOAD/Reshapr/issues
    ( pkg_development: line   58) ok        https://www.python.org/
    ( pkg_development: line  145) ok        https://www.python.org/dev/peps/pep-0008/
    ( pkg_development: line   66) ok        https://www.python.org/dev/peps/pep-0636/
    ( pkg_development: line  178) ok        https://www.sphinx-doc.org/en/master/
    ( pkg_development: line   22) ok        https://readthedocs.org/projects/Reshapr/badge/?version=latest
    ( pkg_development: line  178) ok        https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
    (design_notes/motivation: line   53) ok        https://xarray.pydata.org/en/latest/
    (design_notes/motivation: line   65) ok        https://xarray.pydata.org/en/latest/generated/xarray.open_mfdataset.html#xarray.open_mfdataset
    ( pkg_development: line  172) ok        https://readthedocs.org/projects/reshapr/badge/?version=latest
    (design_notes/motivation: line  128) ok        https://github.com/UBC-MOAD/Reshapr
    build succeeded.

Look for any errors in the above output or in _build/linkcheck/output.txt


.. _ReshaprRunningTheUnitTests:

Running the Unit Tests
======================

The test suite for the :py:obj:`Reshapr` package is in :file:`Reshapr/tests/`.
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

    ================================ test session starts =================================
    platform linux -- Python 3.10.2, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
    Using --randomly-seed=2578159981
    rootdir: /media/doug/warehouse/MOAD/Reshapr
    plugins: randomly-3.11.0, cov-3.0.0
    collected 7 items

    tests/core/test_dask_cluster.py .......                                         [100%]

    ================================== 7 passed in 1.60s =================================

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

to produce an HTML report that you can view in your browser by opening
:file:`Reshapr/htmlcov/index.html`.


.. _SalishSeaNowcastContinuousIntegration:

Continuous Integration
----------------------

.. image:: https://github.com/UBC-MOAD/Reshapr/workflows/CI/badge.svg
    :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow%3ACI
    :alt: pytest and test coverage analysis
.. image:: https://codecov.io/gh/UBC-MOAD/Reshapr/branch/main/graph/badge.svg
    :target: https://app.codecov.io/gh/UBC-MOAD/Reshapr
    :alt: Codecov Testing Coverage Report

The :py:obj:`Reshapr` package unit test suite is run and a coverage report is generated
whenever changes are pushed to GitHub.
The results are visible on the `repo actions page`_,
from the green checkmarks beside commits on the `repo commits page`_,
or from the green checkmark to the left of the "Latest commit" message on the
`repo code overview page`_ .
The testing coverage report is uploaded to `codecov.io`_

.. _repo actions page: https://github.com/UBC-MOAD/Reshapr/actions
.. _repo commits page: https://github.com/UBC-MOAD/Reshapr/commits/main
.. _repo code overview page: https://github.com/UBC-MOAD/Reshapr
.. _codecov.io: https://app.codecov.io/gh/UBC-MOAD/Reshapr

The `GitHub Actions`_ workflow configuration that defines the continuous integration tasks
is in the :file:`.github/workflows/pytest-coverage.yaml` file.

.. _GitHub Actions: https://docs.github.com/en/actions


.. _ReshaprVersionControlRepository:

Version Control Repository
==========================

.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr
    :alt: Git on GitHub

The :py:obj:`Reshapr` package code and documentation source files are available
as a `Git`_ repository at https://github.com/UBC-MOAD/Reshapr.

.. _Git: https://git-scm.com/


.. _ReshaprIssueTracker:

Issue Tracker
=============

.. image:: https://img.shields.io/github/issues/UBC-MOAD/Reshapr?logo=github
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
