.. image:: https://travis-ci.org/comtihon/catcher.svg?branch=master
    :target: https://travis-ci.org/comtihon/catcher
.. image:: https://img.shields.io/pypi/v/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://img.shields.io/pypi/pyversions/catcher_modules.svg
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
Catcher is a flexible tool, that can be used for: automated end-to-end testing, running universal migrations, 
performing complex business actions.  
It helps you to check either one service or whole system interaction.
With the help of Catcher you can easily mock external services your system relies on. Catcher is not about only http, it
can check Kafka, Postgres, CouchBase, Mongodb.


Testing - How it works?
-----------------------

1. You implement new business requirements, touching one ore more services (external and internal)
2. You write `tests`_ file in `YAML`_ or `JSON`_ formats where you describe data movement in your system
3. You run your tests in any environment (from dev to prod) just changing `inventory`_ files.
4. Bob (your colleague) implements his own business logic, which requires your test (or part of it) to be run.
5. Bob writes his test in YAML and includes your test (or certain steps) to be run before or during his test.
6. John (your devOps) decides to automate tests and makes CI run all tests on every microservice deploy.
7. Your business logic is tested automatically and you will know if some of your services interact incorrectly.
8. Profit.

.. _YAML: https://wikipedia.org/wiki/YAML
.. _JSON: https://www.json.org/
.. _inventory: https://catcher-test-tool.readthedocs.io/en/latest/source/inventory.html
.. _tests: https://catcher-test-tool.readthedocs.io/en/latest/source/tests.html


Migration - How it works?
-------------------------
Every new feature in microservices require several migration steps in more than one service. But it is much better to
create one migration script for all services (kafka, aws, databases) to prevent code duplication and keep all instructions
in one place. See more in `migrations`_

.. _migrations: https://catcher-test-tool.readthedocs.io/en/latest/source/migrations.html


Complex business actions - How it works?
----------------------------------------
| If in your company you need to perform some complex business actions - use catcher to automate them.
| F.e. before business review you need to register a new user and it requires you to make 10 http request and send 2 kafka messages.
| Do you really like to spend 10-20 minutes of your time on doing these steps one by one?
| Write a catcher script `register_new_user.yaml` and call it manually:
| `catcher -i inventory.yaml register_new_user.yaml -e user_name=test_22.04.2018`.


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

New in `1.19.0`:

| To have `docker-compose` support install `catcher[compose]` instead.
| This will make catcher run `docker-compose up` in your resources directory, if docker-compose file was found.

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

.. _module: https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html

Why catcher?
------------

* don't repeat test code. Write one test and call its steps from another;
* compute and override variables to check your data and compose new flexible requests;
* apply :meth:`catcher.steps.check` to the steps results;
* write test for development, change inventory and test stage/uat/prod after deploy;
* test all your `microservices`_ with ease;
* automate your testing!
* `modular`_ architecture

Quickstart and documentation
----------------------------
See `readthedocs`_.

.. _readthedocs: https://catcher-test-tool.readthedocs.io/en/latest/
.. _microservices: https://catcher-test-tool.readthedocs.io/en/latest/source/microservices.html
.. _modular: https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html
