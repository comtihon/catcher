*********************************
Installation and run instructions
*********************************

Local
=====
Local run requires Catcher to be installed first.

Python installation
-------------------

| Catcher was developed in Python3 and is delivered as a Python's Pip package. Make sure you have both **python** and **pip**
 executable available in the system. In some systems they are called **python3** and **pip3**.
| Run `python --version` to get current python's version

| **Recommended way**
| If you don't have python 3.5+ version available or don't want to use system's python - you can use
 `conda <https://docs.conda.io/en/latest/miniconda.html>`_ to install local python environment.

1. install conda executable.
See official `doc <https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation>`_ for more info

for Linux::

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh

| 2. create conda environment

for Linux::

    conda create --name catcher python=3.7

| 3. activate environment

for Linux::

    conda activate catcher
    python --version

Now you have local python37 installation which you can use after activation.

Catcher installation
--------------------
| Catcher has 2 python packages: the `core <https://pypi.org/project/catcher/>`_ which contains most basic steps, executable
 and core logic and the external `modules <https://pypi.org/project/catcher-modules/>`_ package which contains external modules
 like database, message queue, aws services and other tools support.
| To install the core - run `pip install catcher`. After it you should be able to run catcher from command line. Check it
 with `catcher -h`.
| **Important:** if you are using conda - make sure you installed Catcher in the environment and that the environment is
 activated every time you are going to run Catcher.

| External modules are installed separately on demand, as probably you don't need all of them. Also, some external modules
 require drivers and client libraries, needed to be installed locally as well (see readme for more information). F.e. to
 install only kafka module you need to run `pip install catcher-modules[kafka]`. In case you need multiple modules - use
 comma to separate them: `pip install catcher-modules[kafka,s3]`

Run Catcher
-----------
| By default all Catcher resources are in `./resources` directory. They are used in steps (http/message bodies, data for queries, selenium source files).
| `Inventory`_ files are in `./inventory`. They are used for environment specific variables like database configuration and services endpoints.
| `Substeps`_ are in `./steps`. They are part of the tests, written in Catcher to be included in tests.
| `Tests`_ are in `./tests`. They are your tests.
| `Reports`_ are in `./reports`. This directory is stored for Catcher tests traces. See :doc:`reports` for more info.

.. _Substeps: https://catcher-test-tool.readthedocs.io/en/latest/source/includes.html
.. _Inventory: https://catcher-test-tool.readthedocs.io/en/latest/source/inventory.html
.. _Tests: https://catcher-test-tool.readthedocs.io/en/latest/source/tests.html
.. _Reports: https://catcher-test-tool.readthedocs.io/en/latest/source/reports.html

| To run you test use `catcher tests`. It will run all tests in `tests` directory and subdirectories. You can specify
 the exact test to run it individually: `catcher tests/my_test.yml`.

Docker
======

Docker run doesn't require Catcher or Python to be installed. Catcher's docker image will be pulled by Docker automatically.
Just make sure you have Docker installed.

| It is the most convenient way to run tests. Catcher offers you docker 2 images: `catcher_base`_ and `catcher`_.
| catcher_base is the base image with only catcher-core installed. You can use it to build your own docker image.
| catcher is the full, ready to use image with Catcher and all modules from catcher-modules installed.

.. _catcher_base: https://hub.docker.com/repository/docker/comtihon/catcher_base
.. _catcher: https://hub.docker.com/repository/docker/comtihon/catcher

| Catcher image supports `tests`, `resources`, `inventory`, `steps` and `reports` for formatted reports.
 Mount your directories during the run to use them. The full command where everything is used will look like this:

::

    docker run -v $(pwd)/inventory:/opt/catcher/inventory
               -v $(pwd)/resources:/opt/catcher/resources
               -v $(pwd)/tests:/opt/catcher/tests
               -v $(pwd)/steps:/opt/catcher/steps
               -v $(pwd)/reports:/opt/catcher/reports
                catcher -i inventory/my_inventory.yml tests

