# Microservices automated test tool
[![Build Status](https://travis-ci.org/comtihon/catcher.svg?branch=master)](https://travis-ci.org/comtihon/catcher)
[![PyPI](https://img.shields.io/pypi/v/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/pyversions/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/wheel/catcher.svg)](https://pypi.python.org/pypi/catcher)  
Support your team with a good Catcher!  
## What is catcher?
Catcher is a flexible tool, that can be used for: automated end-to-end testing, running universal migrations, 
performing complex business actions.  
It helps you to check either one service or whole system interaction.
With the help of Catcher you can easily mock external services your system relies on. Catcher is not about only http, it
can check Kafka, Postgres (coming soon), CouchBase (coming soon), Mongodb (coming soon).

## Testing - How it works?
1. You implement new business requirements, touching one ore more services (external and internal)
2. You write [test](doc/tests.md) file in [YAML](https://de.wikipedia.org/wiki/YAML) format where you describe data movement in your system
3. You run your tests in any environment (from dev to prod) just changing [inventory](doc/inventory.md) files.
4. Bob (your colleague) implements his own business logic, which requires your test (or part of it) to be run.
5. Bob writes his test in YAML and includes your test (or certain steps) to be run before or during his test.
6. John (your devOps) decides to automate tests and makes CI run all tests on every microservice deploy.
7. Your business logic is tested automatically and you will know if some of your services interact incorrectly.
8. Profit. 
## Migration - How it works?
Every new feature in microservices require several migration steps in more than one service. But it is much better to
create one migration script for all services (kafka, aws, databases) to prevent code duplication and keep all instructions
in one place. See more in [migrations](doc/migrations.md)
## Complex business actions - How it works?
If in your company you need to perform some complex business actions - use catcher to automate them. F.e. before business 
review you need to register a new user and it requires you to make 10 http request and send 2 kafka messages. Do you really
like to spend 10-20 minutes of your time on doing these steps one by one? Write a catcher script `register_new_user.yaml`
and call it manually `catcher -i inventory.yaml register_new_user.yaml -e user_name=test_22.04.2018`.

## Why catcher?
* don't repeat test code. Write one test and call its steps from another;
* compute and override variables to check your data and compose new flexible requests;
* apply [checks](doc/checks.md) to the steps results;
* write test for development, change inventory and test stage/uat/prod after deploy;
* test all your [microservices](doc/microservices.md) with ease;
* automate your testing!
* [modular](doc/modules.md) architecture

## Variables override
1. Test's variables override inventory's variables.
2. Variables from include don't go to main test file.

## Running checks
see [checks](doc/checks.md) for details.

## Quickstart
Is [here](doc/tests.md). For more information please refer to [tests](test) folder.