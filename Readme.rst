.. image:: https://travis-ci.org/comtihon/catcher.svg?branch=master
    :target: https://travis-ci.org/comtihon/catcher
.. image:: https://img.shields.io/pypi/v/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://img.shields.io/pypi/pyversions/catcher_modules.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://img.shields.io/pypi/wheel/catcher.svg
    :target: https://pypi.python.org/pypi/catcher

.. |br| raw:: html

Microservices automated test tool
=================================
Support your team with a good Catcher!  


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
2. You write [test](doc/tests.md) file in `YAML`_ format where you describe data movement in your system
3. You run your tests in any environment (from dev to prod) just changing [inventory](doc/inventory.md) files.
4. Bob (your colleague) implements his own business logic, which requires your test (or part of it) to be run.
5. Bob writes his test in YAML and includes your test (or certain steps) to be run before or during his test.
6. John (your devOps) decides to automate tests and makes CI run all tests on every microservice deploy.
7. Your business logic is tested automatically and you will know if some of your services interact incorrectly.
8. Profit.

.. _YAML: https://de.wikipedia.org/wiki/YAML

Migration - How it works?
-------------------------
Every new feature in microservices require several migration steps in more than one service. But it is much better to
create one migration script for all services (kafka, aws, databases) to prevent code duplication and keep all instructions
in one place. See more in [migrations](doc/migrations.md)


Complex business actions - How it works?
----------------------------------------
If in your company you need to perform some complex business actions - use catcher to automate them. |br|
F.e. before business review you need to register a new user and it requires you to make 10 http request and send 2 kafka messages. |br|
Do you really like to spend 10-20 minutes of your time on doing these steps one by one? |br|
Write a catcher script `register_new_user.yaml` and call it manually: |br|
`catcher -i inventory.yaml register_new_user.yaml -e user_name=test_22.04.2018`.


Installation
------------
To install catcher with internal `modules`_ run `sudo pip install catcher-modules`. |br|
This will install `catcher`_ and `catcher-modules`_ package. |br|
To install just catcher run `sudo pip install catcher`.

.. _catcher: https://pypi.org/project/catcher
.. _modules: https://github.com/comtihon/catcher_modules
.. _catcher-modules: https://pypi.org/project/catcher-modules


Why catcher?
------------

* don't repeat test code. Write one test and call its steps from another;
* compute and override variables to check your data and compose new flexible requests;
* apply [checks](doc/checks.md) to the steps results;
* write test for development, change inventory and test stage/uat/prod after deploy;
* test all your [microservices](doc/microservices.md) with ease;
* automate your testing!
* [modular](doc/modules.md) architecture

Quickstart and documentation
----------------------------
See `readthedocs`_.

.. _readthedocs: https://catcher-modules.readthedocs.io/en/latest/
