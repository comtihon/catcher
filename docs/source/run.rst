Local
=====
| Make sure catcher is installed. If not - run `pip install catcher`. This will install basic steps & catcher executable.
| If you need more steps - check out `catcher-modules <https://github.com/comtihon/catcher_modules>`_.
 F.e. `pip install catcher-modules[kafka]`.
| It is highly recommended to keep things separated.
| By default all catcher resources are in `./resources` directory.
| `Inventory`_ files are in `./inventory`, `substeps`_ are in `./steps`, `modules`_ are in `./modules`. `Tests`_ are in `./tests`.

.. _modules: https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html
.. _substeps: https://catcher-test-tool.readthedocs.io/en/latest/source/includes.html
.. _Inventory: https://catcher-test-tool.readthedocs.io/en/latest/source/inventory.html
.. _Tests: https://catcher-test-tool.readthedocs.io/en/latest/source/tests.html

| Run `catcher -h` to check if it is installed and see all options available.
| To run you test use `catcher tests`. It will run all tests in `tests` directory and subdirectories. You can specify
 the exact test to run it individually: `catcher tests/my_test.yml`.
| *Useful hint*: Sometimes it is hard to debug the test, even with `--log-level debug` cmd option. Use `--format json` to
 check the input and output value for every step of your test. *(html format is still in development)*.

Docker
======
| It is the most convenient way to run tests. Catcher offers you docker 2 images: `catcher_base`_ and `catcher`.
| catcher_base is the base image with catcher installed. You can use it to build your own docker image.
| catcher is the full, ready to use image with catcher and all modules from catcher-modules installed.

.. _catcher_base: https://hub.docker.com/repository/docker/comtihon/catcher_base
.. _catcher: https://hub.docker.com/repository/docker/comtihon/catcher

| Catcher image supports `tests`, `resources`, `inventory`, `steps` and `reports` for formatted reports.
 Mount your directories during the run to use them. The full command where everything is used will look like this:

::

    docker run -v $(pwd)/inventory:/opt/catcher/inventory
               -v $(pwd)/resources:/opt/catcher/resources
               -v $(pwd)/test:/opt/catcher/tests
               -v $(pwd)/steps:/opt/catcher/steps
               -v $(pwd)/reports:/opt/catcher/reports
                catcher -i inventory/my_inventory.yml tests

