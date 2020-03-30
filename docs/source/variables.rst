Variables
=========

Predefined
----------
Variables from inventory, ``variables`` block or command line ``-e`` argument

Computed
--------

| Registered in steps variables via ``register: {var_name: var_value}``.
| ``var_value`` can be a variable itself like: ``register: {email: '{{ user }}@test.com'}``

Inherited
---------
Inherited from ``run`` steps. Every run include adds its variables to test scope.

Built-in
--------
| 1. ``OUTPUT`` - operation's output. Can be used for new variables registration

::

    - http:
        post: 
            url: 'http://test.com'
            body: {'id': '{{ id }}', 'action': 'fee'}
        register: {reply: '{{ OUTPUT.id }}'}

| 2. ``ITEM`` - item of a list. Used in ``any`` and ``all`` checks and ``foreach`` loops

::

    variables:
        list: [{n: 1, k: 'a'}, {n: 2, k: 'a'}, {n: 3, k: 'a'}]
    steps:
        - check:
            all:
                of: '{{ list }}'
                equals: {the: '{{ ITEM.k }}', is: 'a'}

| 3. ``NOW_TS`` - return timestamp. **Deprecated**, use function `now_ts()` instead.

::

    steps:
      - echo: {from: '{{ NOW_TS }}', register: {now: '{{ OUTPUT }}'}}

| 4. ``NOW_DT`` - return current date for UTC timezone in ``yyyy-mm-ddTHH:MM:SS0`` format.  **Deprecated**, use function `now()` instead.
| 5. ``RANDOM_STR`` - return random string in uuid format
| 6. ``RANDOM_INT`` - return random int [-2147483648, 2147483648]
| 7. ``TEST_NAME`` - name of the current test
| 8. ``CURRENT_DIR`` - current directory
| 9. ``INVENTORY`` - current inventory filename.
| 10. ``INVENTORY_FILE`` - full path to the current inventory.
| 11. ``RESOURCES_DIR`` - resources directory. Can be specified via ``-r`` param. Default is ``./resources``.

Built-in functions
------------------
| 1. ``random_int()`` - will generate a random int for you. The only difference between ``RANDOM_INT`` is - you can set limits

::

    steps:
        - echo: {from: '{{ random_int(1, 10) }}', to: one.output}  # write a random int between 1 and 10 to the file
        - echo: {from: '{{ random_int(1) }}', to: one.output} # write a random int from 1 to max_size to the file
        - echo: {from: '{{ random_int(range_to=1) }}', to: one.output} # write a random int from min_size to 1 to the file

| 2. ``random_choice()`` - syntax sugar for ``{{ list[random_var] }}``. Take random element from a list

::

    variables:
        my_list: ['one', 'two', 'three']
    steps:
        - echo: {from: '{{ random_choice(my_list) }}', to: one.output}

| 3. `Faker <https://github.com/joke2k/faker>`_ random data. With all available built-in providers imported. Type of the random data is set as an argument

::

    steps:
        - echo: {from: '{{ random("ipv4_private") }}', to: one.output}  # write random ipv4 address to file
        - echo: {from: '{{ random("name") }}', to: one.output}  # write random name to file
        - echo: {from: '{{ random("address") }}', to: one.output}  # write random address to file
        - echo: {from: '{{ random("email") }}', to: one.output}  # write random email to file

Please see `providers <https://faker.readthedocs.io/en/stable/providers.html>`_ for more info.

| 4. ``hash(algorithm)`` - hash the data using selected algorithm. Please check `hashlib <https://docs.python.org/3/library/hashlib.html>`_ docs for all algorithms available.

::

    variables:
        my_var: 'my_value'
    steps:
        - echo: {from: '{{ "test" | hash("sha1") }}', register: {sha1: '{{ OUTPUT }}'}}
        - echo: {from: '{{ my_var | hash("md5") }}', register: {md5: '{{ OUTPUT }}'}}

Custom functions and filters
----------------------------
If you need some customisation but don't want to create a custom module - you can try a filter/function. Please
check this `page <https://catcher-test-tool.readthedocs.io/en/latest/source/filters_and_functions.html>`_ for more info.

Environment variables
---------------------

| There is a full support for environment variables in inventory files and in steps.
| In steps you can just access them.

::

    steps:
        - check: {equals: {the: '{{ FOO }}', is: '1'}}

| If you run ``export FOO=1`` before - this step will pass.
| Since `1.21.2` predefined variables support templates as well.

::

    variables:
        foo: '{{ FOO }}'
    steps:
        - check: {equals: {the: '{{ foo }}', is: '1'}}

| Because here there are 2 steps:

1. replace foo with ``{{ FOO }}``
2. replace ``{{ FOO }}`` with value from environment.

| However, there is no such limitation in inventory.

inventory.yml ::

    example_host: http://example.com
    database_conf:
            host: '{{ DB_HOST }}'
            dbname: '{{ DB_NAME }}'
            user: '{{ DB_USER }}'
            password: '{{ DB_PASSWORD }}'

test.yml ::

    postgres:
    request:
        conf: '{{ database_conf }}'
        query: 'select count(*) from test'

Variables override priority
===========================

Variables from command line
---------------------------
Variables, passed from command line override inventory variables.
``inventory.yaml``::

    foo=bar

in this case ``catcher -i inventory.yaml test -e foo=baz`` foo variable will be ``baz``.

Variables in test scripts
-------------------------
Variables, set in test scripts, override inventory variables and variables,
passed from command line.
``inventory.yaml``::

    foo: bar

``test.yaml``::

    variables:
        foo: bax
    steps:
        ...

in this case ``catcher -i inventory.yaml test.yaml -e foo=baz`` foo variable will be ``bax``.

Variables from run includes
---------------------------
Variables, computed via ``run`` includes override variables declared before.

``compute_fee.yaml``::

    ---
    variables:
      deposit: 50
    steps:
        - echo: {from: '{{ RANDOM_STR }}', register: {uuid: '{{ OUTPUT }}'}}
        # ... do something else

``main_test.yaml``::

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

Environment variables
---------------------
| All other variables override environmental variables from steps.
| ``export FOO=bar``
test.yml::

    variables:
        FOO: baz
    steps:
        - check: {equals: {the: '{{ FOO }}', is: 'baz'}}

I recommend to use lowercase for your variables and uppercase for environmental.