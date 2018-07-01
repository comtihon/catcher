.. Catcher documentation master file, created by
   sphinx-quickstart on Sun Jul  1 11:54:49 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Catcher's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Intro
=====
Catcher is a flexible tool, that can be used for: automated end-to-end testing, running universal migrations, performing complex business actions.
It helps you to check either one service or whole system interaction. With the help of Catcher you can easily mock external services your system relies on.
Catcher is not about only http, it can check Kafka, Postgres (coming soon), CouchBase (coming soon), Mongodb (coming soon).


Testing
=======

- You implement new business requirements, touching one ore more services (external and internal)
- You write test file in YAML format where you describe data movement in your system
- You run your tests in any environment (from dev to prod) just changing inventory files.
- Bob (your colleague) implements his own business logic, which requires your test (or part of it) to be run.
- Bob writes his test in YAML and includes your test (or certain steps) to be run before or during his test.
- John (your devOps) decides to automate tests and makes CI run all tests on every microservice deploy.
- Your business logic is tested automatically and you will know if some of your services interact incorrectly.
- Profit.

Migration
=========

Every new feature in microservices require several migration steps in more than one service.
But it is much better to create one migration script for all services (kafka, aws, databases) to prevent code duplication and keep all instructions in one place.

Why Catcher?
============
- don't repeat test code. Write one test and call its steps from another;
- compute and override variables to check your data and compose new flexible requests;
- apply :doc:`catcher.steps.html#module-catcher.steps.check` to the steps results;
- write test for development, change inventory and test stage/uat/prod after deploy;
- test all your :ref:`microservices` with ease;
- automate your testing!
- :doc:`modules` architecture

Quickstart
==========
* Install Catcher standalone via `sudo pip install catcher` or with additional modules `sudo pip install catcher-modules`.
* Create your tests :doc:`tests`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
