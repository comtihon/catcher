# Microservices automated test tool
[![Build Status](https://travis-ci.org/comtihon/catcher.svg?branch=master)](https://travis-ci.org/comtihon/catcher)
[![PyPI](https://img.shields.io/pypi/v/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/pyversions/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/wheel/catcher.svg)](https://pypi.python.org/pypi/catcher)  
Support your team with a good catcher!  
_What is catcher?_    
Catcher is a tool for automated tests.  
_How it works?_  
Just like ansible for deployment. You create [inventories](doc/inventory.md) for environments,
write test [scenarios](doc/tests.md) for business logic and call catcher.  
_Where it can be useful?_  
Catcher is useful for black box testing, integration testing. And it is extremely useful for 
microservices end-to-end testing!  

## Why catcher?
* don't repeat test code. Write one test and call its steps from another.
* apply [checks](doc/checks.md) to the steps results.
* write test for development, change inventory and test stage/uat/prod after deploy.
* test all your [microservices](doc/microservices.md) with ease.
* automate your testing!

## Variables override
1. Test's variables override inventory's variables.
2. Variables from include don't go to main test file.

## Running checks
see [checks](doc/checks.md) for details.

## Running test steps
* ignore erros

## Built-in variables
1. `OUTPUT` - operation's output. Can be used for new variables registration:
```yaml
    - http: 
        post: 
            url: 'http://test.com'
            body: {'id': '{{ id }}', 'action': 'fee'}
        register: {reply: '{{ OUTPUT.id }}'}
```
2. `ITEM`
3. `NOW_TS`
3. `NOW_DT`
3. `RANDOM_STR`
3. `RANDOM_INT`

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