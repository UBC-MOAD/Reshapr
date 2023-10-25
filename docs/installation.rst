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


************
Installation
************

Get the Code
============

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


Conda Environment and Package Installation
==========================================

Running :py:obj:`Reshapr` in an isolated `Conda`_ environment using is highly recommended.
Assuming that you have `Miniconda3`_ installed,
you can create and activate an environment called :kbd:`reshapr` that will have
all of the Python packages necessary use :py:obj:`Reshapr`,
and install the package with the commands below.

.. _Conda: https://conda.io/en/latest/
.. _Miniconda3: https://docs.conda.io/en/latest/miniconda.html

.. code-block:: bash

    $ cd Reshapr
    $ conda env create -f envs/environment-user.yaml
    $ conda activate reshapr

:py:obj:`Reshapr` is installed in `editable install mode`_ as part of the conda environment
creation process.
That means that the package is installed from the cloned repo via symlinks so that
it will be automatically updated as the repo evolves.
Please see :ref:`ReshaprUpdateInstallation` for more details.

.. _editable install mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

You can confirm that you have successfully installed :py:obj:`Reshapr`
by typing :kbd:`reshapr` in your activated environment.
You should see the top level command help information and the list of available
:ref:`ReshaprSubcommands`.

You can show the version of :py:obj:`Reshapr` that you have installed
and other important information with:

.. code-block:: bash

    (reshapr)$ reshapr info

To deactivate the environment use:

.. code-block:: bash

    (reshapr)$ conda deactivate

.. note::
    If you want to make code changes in the :py:obj:`Reshapr` package,
    please see :ref:`ReshaprPackagedDevelopment` for information on how to work in
    the package development environment.

If you want to use :py:obj:`Reshapr` in a different `Conda`_ environment,
edit your environment description to include the packages listed in the
:kbd:`dependencies:` section of :file:`envs/environment-user.yaml`,
then update your environment and install :py:obj:`Reshapr` with:

.. code-block:: bash

    (your-env)$ conda env update -f your-env-yaml
    (your-env)$ python3 -m pip install --editable path/to/Reshapr


.. _ReshaprUpdateInstallation:

Updating Your Installation
==========================

In general,
all you need to do to update your :py:obj:`Reshapr` installation is pull the latest updates
from GitHub:

.. code-block:: bash

    $ cd Reshapr
    $ conda activate reshapr
    (reshapr)$ git pull

You may also need to do:

.. code-block:: bash

    (reshapr)$ python3 -m pip install --editable .

to complete the update if there have been new :ref:`ReshaprSubcommands` or options
added since your last update.


Uninstalling
============

If you want to uninstall :py:obj:`Reshapr`,
you can remove the `Conda`_ environment with:

.. code-block:: bash

    $ conda env remove -n reshapr

You can remove your clone of the `repository`_ with:

.. code-block:: bash

    $ cd Reshapr/..
    $ rm -rf Reshapr/
