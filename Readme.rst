.. image:: https://travis-ci.org/comtihon/catcher.svg?branch=master
    :target: https://travis-ci.org/comtihon/catcher
.. image:: https://img.shields.io/pypi/v/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://img.shields.io/pypi/pyversions/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://img.shields.io/pypi/wheel/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://patrolavia.github.io/telegram-badge/chat.png
    :target: https://t.me/catcher_e2e

Microservices automated test tool
=================================
Support your team with a good Catcher!

.. image:: https://raw.githubusercontent.com/comtihon/catcher/master/docs/_static/logo_big.png
   :scale: 50 %

What is catcher?
----------------
Catcher is a flexible end to end test tool, that can be used for automated microservices or data pipelines testing.
It helps you to check either one service or whole system interaction.
With the help of Catcher you can easily mock external services your system relies on. Catcher is not about only http, it
can check different services, such as Kafka, Postgres, CouchBase, Mongodb, Elastic, S3, emails and others.

Testing - How it works?
-----------------------

1. You implement new business requirements, touching one ore more services (external and internal)
2. You write `tests`_ file in `YAML`_ or `JSON`_ formats where you describe data movement in your system
3. You run your tests in any environment (from dev to prod) by just changing `inventory`_ files.
4. Bob (your colleague) implements his own business logic, which requires your test (or part of it) to be run.
5. Bob writes his test in YAML and `includes`_ your test (or certain steps) to be run before or during his test.
6. John (your devOps) decides to automate tests and makes CI run all tests on every microservice deploy.
7. Your business logic is tested automatically and you will know if some of your services interact incorrectly.
8. Profit.

.. _YAML: https://wikipedia.org/wiki/YAML
.. _JSON: https://www.json.org/
.. _inventory: https://catcher-test-tool.readthedocs.io/en/latest/source/inventory.html
.. _tests: https://catcher-test-tool.readthedocs.io/en/latest/source/tests.html
.. _includes: https://catcher-test-tool.readthedocs.io/en/latest/source/includes.html


Installation
------------
| To install catcher with all internal `modules`_ run `sudo pip install catcher-modules[all]`.
| This will install `catcher`_ and `catcher-modules`_ package.
| To install just catcher run `sudo pip install catcher`.
| To install specific catcher-module use `pip install catcher-modules[kafka]`. See `catcher-modules-index`_ for all
  available modules.

.. _catcher: https://pypi.org/project/catcher
.. _modules: https://github.com/comtihon/catcher_modules
.. _catcher-modules: https://pypi.org/project/catcher-modules
.. _catcher-modules-index: https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.html#module-catcher_modules

Changelog is `here <https://github.com/comtihon/catcher/blob/master/Changelog.rst>`_.

Customization
-------------
Catcher can be easily customized to serve your needs.

1. You can write your own functions and filters and use them in your step's `templates <https://catcher-test-tool.readthedocs.io/en/latest/source/filters_and_functions.html>`_.
2. You can create your own `steps <https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html>`_ (as python script or any executable)
3. You can write your steps in catcher itself and `include <https://catcher-test-tool.readthedocs.io/en/latest/source/includes.html#run-on-action>`_ them from other tests.

Usage
-----
* Write catcher script (see `tests`_). F.e.::

    ---
    steps:
    - http: {get: {url: 'http://my_cache_service.com/save?key=foo&value=bar'}}
    - redis:
        request:
            get: 'foo'
        register: {foo: '{{ OUTPUT }}'}
    - check:
        equals: {the: '{{ foo }}', is: 'bar'}

* Run catcher `catcher my_test_file.yml`.

| You can also specify `inventory`_ with `-i` to test against different environments, custom `module`_ paths with `-m`
  to include your own modules. Run `catcher -h` to get full list of available options.
| See `run`_ documentation for local & docker run info.

.. _module: https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html
.. _run: https://catcher-test-tool.readthedocs.io/en/latest/source/run.html

Why catcher?
------------

* don't repeat test code. Write one test and call its steps from another;
* compute and override variables to check your data and compose new flexible requests;
* apply :meth:`catcher.steps.check` to the steps results;
* write test for development, change inventory and test stage/uat/prod after deploy;
* test all your `microservices`_ with ease;
* `modular`_ architecture
* perfect for big data `pipelines`_ testing with `prepare-expect`_
* automate your testing!

Quickstart and documentation
----------------------------
See `readthedocs`_.

.. _readthedocs: https://catcher-test-tool.readthedocs.io/en/latest/
.. _microservices: https://catcher-test-tool.readthedocs.io/en/latest/source/microservices.html
.. _modular: https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html
.. _prepare-expect: https://catcher-modules.readthedocs.io/en/latest/source/prepare_expect.html
.. _pipelines: https://catcher-modules.readthedocs.io/en/latest/source/airflow.html
