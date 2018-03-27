# Variables
## Predefined
Variables from inventory or `variables` block.
## Computed
Registered in steps variables
## Inherited
Inherited from `run` steps.
## Built-in
1. `OUTPUT` - operation's output. Can be used for new variables registration:
```yaml
    - http: 
        post: 
            url: 'http://test.com'
            body: {'id': '{{ id }}', 'action': 'fee'}
        register: {reply: '{{ OUTPUT.id }}'}
```
2. `ITEM` - item of a list. Used in `any` and `all` checks:
```yaml
variables:
    list: [{n: 1, k: 'a'}, {n: 2, k: 'a'}, {n: 3, k: 'a'}]
steps:
    - check: 
        all:
            of: '{{ list }}'
            equals: {the: '{{ ITEM.k }}', is: 'a'}
```
3. `NOW_TS` - return timestamp:
```yaml
steps:
  - echo: {from: '{{ NOW_TS }}', register: {now: '{{ OUTPUT }}'}}
```
3. `NOW_DT` - return current date in `yyyy-mm-ddTHH:MM:SS0+0000`
3. `RANDOM_STR` - return random string in uuid format
3. `RANDOM_INT` - return random int [-2147483648, 2147483648]

## Variables override priority

### Variables from run includes
Variables, computed via `run` includes override variables declared before:

`compute_fee.yaml`
```yaml

---
variables:
  deposit: 50
steps:
    - echo: {from: '{{ RANDOM_STR }}', register: {uuid: '{{ OUTPUT }}'}}
    # ... do something else
```

`main_test.yaml`
```yaml

---
include: 
    file: compute_fee.yaml
    as: compute_fee
variables:
    deposit: 100
steps:
    - echo: {from: 'test_user', register: {uuid: '{{ OUTPUT }}'}}
    - check: {equals: {the: '{{ deposit }}', is: 100}}  # deposit is 100, as we set up in variables
    - check: {equals: {the: '{{ uuid }}', is: 'test_user'}}  # uuid is the same we registered several steps above
    - run: compute_fee
    - check: {equals: {the: '{{ deposit }}', is: 50}}  # deposit is 50, computed from compute_fee run
    - check: {equals: {the: '{{ uuid }}', is_not: 'test_user'}}  # uuid is random, got from compute_fee run
```