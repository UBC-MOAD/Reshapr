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

:py:obj:`Reshapr` uses Pixi_ for dependency and environment management.
If you don't already have Pixi_ installed,
please follow its `installation instructions`_ to do so.

.. _Pixi: https://pixi.prefix.dev/latest/
.. _`installation instructions`: https://pixi.prefix.dev/latest/installation/


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


Package Installation
====================

Use Pixi to create an isolated environment for :py:obj:`Reshapr` to avoid conflicts with
other Python packages installed on your system.
That environment will have all of the Python packages necessary to use the :program:`reshapr`
command that is provided by the :py:obj:`Reshapr` package.

.. code-block:: console

    $ cd Reshapr
    $ pixi install

When you are in the :file:`Reshapr/` directory
(or a sub-directory)
you can run the :program:`reshapr` command with with the :command:`pixi run` command.
Example:

.. code-block:: console

    $ pixi run reshapr help

You can show the version of :py:obj:`Reshapr` that you have installed
and other important information with:

.. code-block:: bash

    $ pixi run reshapr info

For doing development,
testing,
and documentation of the :py:obj:`Reshapr` package,
please see the :ref:`ReshaprDevelopmentEnvironment` section.


.. _ReshaprUpdateInstallation:

Updating Your Installation
==========================

In general,
all you need to do to update your :py:obj:`Reshapr` installation is pull the latest updates
from GitHub:

.. code-block:: bash

    $ cd Reshapr
    $ git pull
    $ pixi install


Uninstalling
============

If you want to uninstall :py:obj:`Reshapr`,
you can remove your clone of the `repository`_ and the Pixi environment with:

.. code-block:: bash

    $ cd Reshapr/..
    $ rm -rf Reshapr/
