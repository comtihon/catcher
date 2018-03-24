# Microservices automated test tool
[![Build Status](https://travis-ci.org/comtihon/catcher.svg?branch=master)](https://travis-ci.org/comtihon/catcher)
[![PyPI](https://img.shields.io/pypi/v/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/pyversions/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/wheel/catcher.svg)](https://pypi.python.org/pypi/catcher)  
Support your team with a good Catcher!  
## What is catcher?
Catcher is a tool for automated end-to-end tests. It helps you to check either one service or whole system interaction.
With the help of Catcher you can easily mock external services your system relies on. Catcher is not about only http, it
can check Kafka, Postgres (coming soon), CouchBase (coming soon), Mongodb (coming soon).

## How it works?
1. You implement new business requirements, touching one ore more services (external and internal)
2. You write [test](doc/tests.md) file in [YAML](https://de.wikipedia.org/wiki/YAML) format where you describe data movement in your system
3. You run your tests in any environment (from dev to prod) just changing [inventory](doc/inventory.md) files.
4. Bob (your colleague) implements his own business logic, which requires your test (or part of it) to be run.
5. Bob writes his test in YAML and includes your test (or certain steps) to be run before or during his test.
6. John (your devOps) decides to automate tests and makes CI run all tests on every microservice deploy.
7. Your business logic is tested automatically and you will know if some of your services interact incorrectly.
8. Profit. 

## Why catcher?
* don't repeat test code. Write one test and call its steps from another;
* compute and override variables to check your data and compose new flexible requests;
* apply [checks](doc/checks.md) to the steps results;
* write test for development, change inventory and test stage/uat/prod after deploy;
* test all your [microservices](doc/microservices.md) with ease;
* automate your testing!

## Variables override
1. Test's variables override inventory's variables.
2. Variables from include don't go to main test file.

## Running checks
see [checks](doc/checks.md) for details.

## Running test steps
* ignore erros

## Include variables priority:
1. include variables override everything (inventory, variables form previous includes and variables
set in include test file).
```yaml
include: 
    - file: 'run_me_with_override.yaml'
      variables:
        user_email: john.doe@test.de
```
`{{ user_email }}` will be `john.doe@test.de` even if `user_email` is also set in inventory with other
value, or was computed in previous include file, or is set in file `run_me_with_override.yaml`.
2. include's file variables override variables from previous include.  
`include1.yaml`
```yaml
variables:
    foo: bar
steps:
    - echo: {from: '{{ foo }}'}
```
`include2.yaml`
```yaml
variables:
    foo: baz
steps:
    - echo: {from: '{{ foo }}'}
```
`test.yaml`
```yaml
include:
    - 'include1.yaml'
    - 'include2.yaml'
steps:
    - echo: {from: '{{ foo }}'}
```
Will print you:
```
bar
baz

```
`bar` - when `include1.yaml` was included and run,  
`baz` - when `include2.yaml` was included and run,  
nothing - when `test.yaml` was run (variables from includes don't go to test).