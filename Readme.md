# Microservices automated test tool
[![Build Status](https://travis-ci.org/comtihon/catcher.svg?branch=master)](https://travis-ci.org/comtihon/catcher)
[![PyPI](https://img.shields.io/pypi/v/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/pyversions/catcher.svg)](https://pypi.python.org/pypi/catcher)
[![PyPI](https://img.shields.io/pypi/wheel/catcher.svg)](https://pypi.python.org/pypi/catcher)  
## Variables override
1. Test's variables override inventory's variables.
2. Variables from include don't go to main test file.

## Running checks
see [checks](doc/checks.md) for details.

## Built-in variables
1. `OUTPUT` - operation's output. Can be used for new variables registration:
```yaml
    - http: 
        post: 
            url: 'http://test.com'
            body: {'id': '{{ id }}', 'action': 'fee'}
        register: {reply: '{{ OUTPUT.id }}'}
```
2. ``

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