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

+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Continuous Integration** | .. image:: https://github.com/UBC-MOAD/Reshapr/actions/workflows/pytest-with-coverage.yaml/badge.svg                                                                                       |
|                            |      :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:pytest-with-coverage                                                                                              |
|                            |      :alt: Pytest with Coverage Status                                                                                                                                                     |
|                            | .. image:: https://codecov.io/gh/UBC-MOAD/Reshapr/branch/main/graph/badge.svg                                                                                                              |
|                            |      :target: https://app.codecov.io/gh/UBC-MOAD/Reshapr                                                                                                                                   |
|                            |      :alt: Codecov Testing Coverage Report                                                                                                                                                 |
|                            | .. image:: https://github.com/UBC-MOAD/Reshapr/actions/workflows/codeql-analysis.yaml/badge.svg                                                                                            |
|                            |     :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:CodeQL                                                                                                             |
|                            |     :alt: CodeQL analysis                                                                                                                                                                  |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Documentation**          | .. image:: https://app.readthedocs.org/projects/reshapr/badge/?version=latest                                                                                                              |
|                            |     :target: https://reshapr.readthedocs.io/en/latest/                                                                                                                                     |
|                            |     :alt: Documentation Status                                                                                                                                                             |
|                            | .. image:: https://github.com/UBC-MOAD/Reshapr/actions/workflows/sphinx-linkcheck.yaml/badge.svg                                                                                           |
|                            |     :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:sphinx-linkcheck                                                                                                   |
|                            |     :alt: Sphinx linkcheck                                                                                                                                                                 |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Package**                | .. image:: https://img.shields.io/github/v/release/UBC-MOAD/Reshapr?logo=github                                                                                                            |
|                            |     :target: https://github.com/UBC-MOAD/Reshapr/releases                                                                                                                                  |
|                            |     :alt: Releases                                                                                                                                                                         |
|                            | .. image:: https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/UBC-MOAD/Reshapr/main/pyproject.toml&logo=Python&logoColor=gold&label=Python |
|                            |      :target: https://docs.python.org/3/                                                                                                                                                   |
|                            |      :alt: Python Version from PEP 621 TOML                                                                                                                                                |
|                            | .. image:: https://img.shields.io/github/issues/UBC-MOAD/Reshapr?logo=github                                                                                                               |
|                            |     :target: https://github.com/UBC-MOAD/Reshapr/issues                                                                                                                                    |
|                            |     :alt: Issue Tracker                                                                                                                                                                    |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Meta**                   | .. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg                                                                                                                      |
|                            |     :target: https://www.apache.org/licenses/LICENSE-2.0                                                                                                                                   |
|                            |     :alt: Licensed under the Apache License, Version 2.0                                                                                                                                   |
|                            | .. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github                                                                                                         |
|                            |     :target: https://github.com/UBC-MOAD/Reshapr                                                                                                                                           |
|                            |     :alt: Git on GitHub                                                                                                                                                                    |
|                            | .. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white                                                                                    |
|                            |     :target: https://pre-commit.com                                                                                                                                                        |
|                            |     :alt: pre-commit                                                                                                                                                                       |
|                            | .. image:: https://img.shields.io/badge/code%20style-black-000000.svg                                                                                                                      |
|                            |     :target: https://black.readthedocs.io/en/stable/                                                                                                                                       |
|                            |     :alt: The uncompromising Python code formatter                                                                                                                                         |
|                            | .. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg                                                                                                                      |
|                            |     :target: https://github.com/pypa/hatch                                                                                                                                                 |
|                            |     :alt: Hatch project                                                                                                                                                                    |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

The Reshapr package (:py:obj:`Reshapr`) is Command-line tool based on Xarray and Dask
for extraction of model variable time series from model products like
SalishSeaCast, HRDPS & CANESM2/CGCM4.


.. _ReshaprPythonVersions:

Python Versions
===============

.. image:: https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/UBC-MOAD/Reshapr/main/pyproject.toml&logo=Python&logoColor=gold&label=Python
    :target: https://docs.python.org/3/
    :alt: Python Version from PEP 621 TOML

The :py:obj:`Reshapr` package is developed and tested using `Python`_ 3.13.
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

.. _Conda: https://docs.conda.io/en/latest/
.. _Miniconda3: https://docs.conda.io/en/latest/miniconda.html

.. code-block:: bash

    $ cd Reshapr
    $ conda env create -f envs/environment-dev.yaml
    $ conda activate reshapr-dev

:py:obj:`Reshapr` is installed in `editable install mode`_ as part of the conda environment
creation process.
That means that the package is installed from the cloned repo via symlinks so that
it will be automatically updated as the repo evolves.

.. _editable install mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

To deactivate the environment use:

.. code-block:: bash

    (reshapr-dev)$ conda deactivate


.. _ReshaprCodingStyle:

Coding Style
============

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://pre-commit.com
   :alt: pre-commit
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter

The :py:obj:`Reshapr` package uses Git pre-commit hooks managed by `pre-commit`_
to maintain consistent code style and and other aspects of code,
docs,
and repo QA.

.. _pre-commit: https://pre-commit.com/

To install the `pre-commit` hooks in a newly cloned repo,
activate the conda development environment,
and run :command:`pre-commit install`:

.. code-block:: bash

    $ cd Reshapr
    $ conda activate reshapr-dev
    (reshapr-dev)$ pre-commit install

.. note::
    You only need to install the hooks once immediately after you make a new clone of the
    `Reshapr repository`_ and build your :ref:`ReshaprDevelopmentEnvironment`.

.. _Reshapr repository: https://github.com/UBC-MOAD/Reshapr


.. _ReshaprBuildingTheDocumentation:

Building the Documentation
==========================

.. image:: https://app.readthedocs.org/projects/reshapr/badge/?version=latest
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
        Running Sphinx v8.1.3
        loading translations [en]... done
        making output directory... done
        loading intersphinx inventory 'arrow' from https://arrow.readthedocs.io/en/latest/objects.inv ...
        loading intersphinx inventory 'dask' from https://docs.dask.org/en/stable/objects.inv ...
        loading intersphinx inventory 'moaddocs' from https://ubc-moad-docs.readthedocs.io/en/latest/objects.inv ...
        loading intersphinx inventory 'python' from https://docs.python.org/3/objects.inv ...
        loading intersphinx inventory 'salishseanowcast' from https://salishsea-nowcast.readthedocs.io/en/latest/objects.inv ...
        loading intersphinx inventory 'xarray' from https://docs.xarray.dev/en/stable/objects.inv ...
        building [mo]: targets for 0 po files that are out of date
        writing output...
        building [html]: targets for 21 source files that are out of date
        updating environment: [new config] 21 added, 0 changed, 0 removed
        reading sources... [100%] subcommands/info
        looking for now-outdated files... none found
        pickling environment... done
        checking consistency... done
        preparing documents... done
        copying assets...
        copying static files...
        Writing evaluated template result to /media/doug/warehouse/MOAD/Reshapr/docs/_build/html/_static/language_data.js
        Writing evaluated template result to /media/doug/warehouse/MOAD/Reshapr/docs/_build/html/_static/basic.css
        Writing evaluated template result to /media/doug/warehouse/MOAD/Reshapr/docs/_build/html/_static/documentation_options.js
        Writing evaluated template result to /media/doug/warehouse/MOAD/Reshapr/docs/_build/html/_static/js/versions.js
        copying static files: done
        copying extra files...
        copying extra files: done
        copying assets: done
        writing output... [100%] subcommands/info
        generating indices... genindex py-modindex done
        highlighting module code... [100%] reshapr.utils.date_formatters
        writing additional pages... search done
        dumping search index in English (code: en)... done
        dumping object inventory... done
        build succeeded, 1 warning.

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

.. image:: https://github.com/UBC-MOAD/Reshapr/actions/workflows/sphinx-linkcheck.yaml/badge.svg
    :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:sphinx-linkcheck
    :alt: Sphinx linkcheck

Sphinx also provides a link checker utility which can be run to find
broken or redirected links in the docs.
With your :kbd:`reshapr-dev)` environment activated,
use:

.. code-block:: bash

    (reshapr-dev))$ cd Reshapr/docs/
    (reshapr-dev)) docs$ make linkcheck

The output looks something like:

.. code-block:: text

        Removing everything under '_build'...
        Running Sphinx v8.1.3
        loading translations [en]... done
        making output directory... done
        loading intersphinx inventory 'arrow' from https://arrow.readthedocs.io/en/latest/objects.inv ...
        loading intersphinx inventory 'dask' from https://docs.dask.org/en/stable/objects.inv ...
        loading intersphinx inventory 'moaddocs' from https://ubc-moad-docs.readthedocs.io/en/latest/objects.inv ...
        loading intersphinx inventory 'python' from https://docs.python.org/3/objects.inv ...
        loading intersphinx inventory 'salishseanowcast' from https://salishsea-nowcast.readthedocs.io/en/latest/objects.inv ...
        loading intersphinx inventory 'xarray' from https://docs.xarray.dev/en/stable/objects.inv ...
        building [mo]: targets for 0 po files that are out of date
        writing output...
        building [linkcheck]: targets for 21 source files that are out of date
        updating environment: [new config] 21 added, 0 changed, 0 removed
        reading sources... [100%] subcommands/info
        looking for now-outdated files... none found
        pickling environment... done
        checking consistency... done
        preparing documents... done
        copying assets...
        copying assets: done
        writing output... [100%] subcommands/info

        (design_notes/pkg_structure: line   68) ok        https://click.palletsprojects.com/en/stable/
        ( pkg_development: line   22) ok        https://black.readthedocs.io/en/stable/
        (design_notes/pkg_structure: line   57) ok        https://click.palletsprojects.com/en/stable/quickstart/#nesting-commands
        (             api: line   31) ok        https://arrow.readthedocs.io/en/latest/api-guide.html#arrow.arrow.Arrow
        ( pkg_development: line   22) ok        https://app.codecov.io/gh/UBC-MOAD/Reshapr
        (    installation: line   50) ok        https://docs.conda.io/en/latest/
        ( pkg_development: line  440) ok        https://coverage.readthedocs.io/en/latest/
        ( pkg_development: line   28) ok        https://codecov.io/gh/UBC-MOAD/Reshapr/branch/main/graph/badge.svg
        (    installation: line   50) ok        https://docs.conda.io/en/latest/miniconda.html
        ( pkg_development: line  493) ok        https://docs.github.com/en/actions
        (  model_profiles: line  221) ok        https://docs.dask.org/en/latest/array-chunks.html
        (    installation: line   39) ok        https://docs.github.com/en/authentication/connecting-to-github-with-ssh
        (design_notes/motivation: line   53) ok        https://docs.dask.org/en/latest/
        ( pkg_development: line  402) ok        https://docs.pytest.org/en/latest/
        (             api: line    3) ok        https://docs.python.org/3/library/constants.html#None
        (             api: line   40) ok        https://docs.python.org/3/library/pathlib.html#pathlib.Path
        ( pkg_development: line   22) ok        https://docs.python.org/3/
        (             api: line   22) ok        https://docs.python.org/3/library/exceptions.html#ValueError
        (             api: line   31) ok        https://docs.python.org/3/library/stdtypes.html#str
        ( pkg_development: line   87) ok        https://docs.python.org/3/reference/lexical_analysis.html#f-strings
        (             api: line   40) ok        https://docs.python.org/3/library/stdtypes.html#dict
        (design_notes/motivation: line   53) ok        https://docs.xarray.dev/en/stable/
        ( pkg_development: line  508) ok        https://git-scm.com/
        (design_notes/motivation: line   65) ok        https://docs.xarray.dev/en/stable/generated/xarray.open_mfdataset.html#xarray.open_mfdataset
        (examples/iona_wastewater_discharge_analysis: line   99) ok        https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/wastewater/extract_biology.yaml
        (design_notes/history: line   52) ok        https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/atlantis_nudge_diatoms.py
        (design_notes/history: line   25) ok        https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/dask_expts.ipynb
        (examples/2xrez_physics_ONC_SCVIP: line   44) ok        https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/2xrez-2017/DeepWaterRenewal.ipynb
        (design_notes/history: line   46) ok        https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/atlantis_nudge_diatoms.ipynb
        ( pkg_development: line   31) ok        https://github.com/UBC-MOAD/Reshapr/actions/workflows/codeql-analysis.yaml/badge.svg
        (examples/iona_wastewater_discharge_analysis: line   95) ok        https://github.com/SalishSeaCast/analysis-doug/blob/main/notebooks/wastewater/model_profiles/SalishSeaCast-202111-wastewater-salish.yaml
        ( pkg_development: line   25) ok        https://github.com/UBC-MOAD/Reshapr/actions/workflows/pytest-with-coverage.yaml/badge.svg
        (design_notes/motivation: line  129) ok        https://github.com/UBC-MOAD/Reshapr
        ( pkg_development: line   38) ok        https://github.com/UBC-MOAD/Reshapr/actions/workflows/sphinx-linkcheck.yaml/badge.svg
        ( pkg_development: line  480) ok        https://github.com/UBC-MOAD/Reshapr/actions
        ( pkg_development: line   22) ok        https://github.com/UBC-MOAD/Reshapr/issues
        ( pkg_development: line   22) ok        https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:CodeQL
        ( pkg_development: line   22) ok        https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:pytest-with-coverage
        ( pkg_development: line   22) ok        https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:sphinx-linkcheck
        ( pkg_development: line   64) ok        https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
        ( pkg_development: line   61) ok        https://img.shields.io/badge/code%20style-black-000000.svg
        (           index: line   48) ok        https://img.shields.io/badge/license-Apache%202-cb2533.svg
        ( pkg_development: line   58) ok        https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
        ( pkg_development: line   55) ok        https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
        ( pkg_development: line   42) ok        https://img.shields.io/github/v/release/UBC-MOAD/Reshapr?logo=github
        ( pkg_development: line   22) ok        https://github.com/pypa/hatch
        ( pkg_development: line   22) ok        https://github.com/UBC-MOAD/Reshapr/releases
        ( pkg_development: line   45) ok        https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/UBC-MOAD/Reshapr/main/pyproject.toml&logo=Python&logoColor=gold&label=Python
        (examples/2xrez_physics_ONC_SCVIP: line   43) ok        https://nbviewer.org/github/SalishSeaCast/analysis-doug/blob/main/notebooks/2xrez-2017/DeepWaterRenewal.ipynb
        ( pkg_development: line   48) ok        https://img.shields.io/github/issues/UBC-MOAD/Reshapr?logo=github
        (design_notes/history: line   46) ok        https://nbviewer.org/github/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/atlantis_nudge_diatoms.ipynb
        (design_notes/history: line   25) ok        https://nbviewer.org/github/SalishSeaCast/analysis-doug/blob/main/notebooks/dask-expts/dask_expts.ipynb
        ( pkg_development: line   91) ok        https://peps.python.org/pep-0636/
        (    installation: line   65) ok        https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
        ( pkg_development: line  480) ok        https://github.com/UBC-MOAD/Reshapr/commits/main
        ( pkg_development: line  440) ok        https://pytest-cov.readthedocs.io/en/latest/
        ( pkg_development: line   22) ok        https://reshapr.readthedocs.io/en/latest/
        ( pkg_development: line   22) ok        https://pre-commit.com
        (examples/iona_wastewater_discharge_analysis: line   47) ok        https://salishsea-nowcast.readthedocs.io/en/latest/workers.html#module-nowcast.workers.split_results
        ( pkg_development: line  176) ok        https://pre-commit.com/
        (    installation: line   39) ok        https://ubc-moad-docs.readthedocs.io/en/latest/ssh_access.html#copyyourpublicsshkeytogithub
        (    installation: line   39) ok        https://ubc-moad-docs.readthedocs.io/en/latest/ssh_access.html#secureremoteaccess
        (           index: line   46) ok        https://www.apache.org/licenses/LICENSE-2.0
        ( pkg_development: line   35) ok        https://app.readthedocs.org/projects/reshapr/badge/?version=latest
        (design_notes/motivation: line   53) ok        https://www.pangeo.io/
        (design_notes/motivation: line   53) ok        https://www.pangeo.io/#ecosystem
        ( pkg_development: line  209) ok        https://www.sphinx-doc.org/en/master/
        ( pkg_development: line  209) ok        https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
        (design_notes/pkg_structure: line   63) ok        https://www.structlog.org/en/stable/index.html
        ( pkg_development: line   83) ok        https://www.python.org/
        (examples/prodigy_model_obs_assignment: line   40) ok        https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2018.00536/full
        build succeeded, 1 warning.

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

        =============================== test session starts ================================
        platform linux -- Python 3.13.5, pytest-8.4.1, pluggy-1.6.0
        Using --randomly-seed=3596862623
        rootdir: /media/doug/warehouse/MOAD/Reshapr
        configfile: pyproject.toml
        plugins: randomly-3.15.0, cov-6.2.1, anyio-4.10.0
        collected 303 items

        tests/api/v1/test_extract_api_v1.py .........                                   [  2%]
        tests/core/test_info.py ...............................                         [ 13%]
        tests/core/test_dask_cluster.py .........                                       [ 16%]
        tests/utils/test_date_formatters.py ...........                                 [ 19%]
        tests/test_cluster_configs.py .....                                             [ 21%]
        tests/test_model_profiles.py .........................................................
        ...............................                                                 [ 50%]
        tests/cli/test_cli.py ..                                                        [ 51%]
        tests/core/test_extract.py ...........................................................
        ......................................................................................
        ...                                                                             [100%]

        =============================== 303 passed in 8.42s ================================

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

.. image:: https://github.com/UBC-MOAD/Reshapr/actions/workflows/pytest-with-coverage.yaml/badge.svg
    :target: https://github.com/UBC-MOAD/Reshapr/actions?query=workflow:pytest-with-coverage
    :alt: Pytest with Coverage Status
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


Release Process
===============

.. image:: https://img.shields.io/github/v/release/UBC-MOAD/Reshapr?logo=github
    :target: https://github.com/UBC-MOAD/Reshapr/releases
    :alt: Releases
.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
    :target: https://github.com/pypa/hatch
    :alt: Hatch project


Releases are done at Doug's discretion when significant pieces of development work have been
completed.

The release process steps are:

#. Use :command:`hatch version release` to bump the version from ``.devn`` to the next release
   version identifier;
   e.g. ``23.1.dev0`` to ``23.1``

#. Commit the version bump

#. Create an annotated tag for the release with :guilabel:`Git -> New Tag...` in PyCharm
   or :command:`git tag -e -a vyy.n`;
   :command:`git tag -e -a v23.1`

#. Push the version bump commit and tag to GitHub

#. Use the GitHub web interface to create a release,
   editing the auto-generated release notes into sections:

   * Features
   * Bug Fixes
   * Documentation
   * Maintenance
   * Dependency Updates

#. Use the GitHub :guilabel:`Issues -> Milestones` web interface to edit the release
   milestone:

   * Change the :guilabel:`Due date` to the release date
   * Delete the "when it's ready" comment in the :guilabel:`Description`

#. Use the GitHub :guilabel:`Issues -> Milestones` web interface to create a milestone for
   the next release:

   * Set the :guilabel:`Title` to the next release version,
     prepended with a ``v``;
     e.g. ``v23.2``
   * Set the :guilabel:`Due date` to the end of the year of the next release
   * Set the :guilabel:`Description` to something like
     ``v23.2 release - when it's ready :-)``
   * Create the next release milestone

#. Review the open issues,
   especially any that are associated with the milestone for the just released version,
   and update their milestone.

#. Close the milestone for the just released version.

#. Use :command:`hatch version minor,dev` to bump the version for the next development cycle,
   or use :command:`hatch version major,minor,dev` for a year rollover version bump

#. Commit the version bump

#. Push the version bump commit to GitHub
