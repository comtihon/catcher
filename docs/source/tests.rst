How to write a test cheat sheet
===============================
:meth:`catcher.core.test.Test` documentation can also be useful.

Create a project structure
--------------------------
| **tests** - Here all the tests will live. Feel free to use subdirectories.
| **inventory** - Place your inventory files here. See :doc:`inventory` for more info.
| **resources** - It is for all resources, which are used in tests: RabbitMQ json messages, Postgres ddl, Selenium Java
 sources, json post bodies and what not. See :doc:`resources` for more info.
| **steps** - Place substeps in this directory. Substeps are Catcher test files which hold common actions, needed in
 different tests. They shouldn't be run standalone, like tests, but they can be included in different tests instead.
 See :doc:`includes` for more info.
| **reports** - Catcher will dump the whole test action log (including variables) here, if you specify `format` parameter.
 Is not mandatory, Catcher will create this directory if needed. See :doc:`reports` for more info.

Check steps you may need
------------------------
Catcher has:

1. built-in steps, which you get with common `catcher <https://github.com/comtihon/catcher>`_ installation
2. external steps from `catcher-modules <https://github.com/comtihon/catcher_modules>`_ package, which you need to install individually
3. custom steps in different languages, which you can use as external on your own. See :doc:`modules` for more info

For 1 and 2 see :doc:`steps`.

Install Catcher
---------------
You have 2 options:

| Install catcher locally. Good option if you are planning to develop catcher tests heavily.
| By running `pip install catcher` you will get the **core** catcher installed. If you need some **external** modules
| like f.e. Kafka, Postgres, S3 you need to install them separately by running `pip install catcher-modules[kafka]`.
| Some external modules require additional drivers and libraries needed to be installed (like oracle or mssql db step).

| If you are just going to give a try or need CI to run Catcher - you can use Catcher's docker
| `image <https://hub.docker.com/repository/docker/comtihon/catcher>`_. It comes with all modules, libraries and drivers already
| included.

See :doc:`run` for more information.

Add one step
------------
To add one step - just populate `steps` array::

    ---
    steps:
        - echo: {from: 'Hello world'}

It is not so useful. Lets add two real steps::

    ---
    steps:
        - http:
            post:
              url: '127.0.0.1/save_data'
              body: {key: '1', data: 'foo'}
        - postgres:
            request:
              conf: 'dbname=test user=test host=localhost password=test'
              sql: 'select * from test where id=1'

But it is still not useful, as we need to check the test's result.

Use variables
-------------
Use defined variables to reduce the number of hard coded values. You can set them up in :doc:`inventory`. or
in the test.

Inventory `test_inventory.yaml`::

    ---
    data_service_url: '127.0.0.1/save_data'
    postgres_conf:
        dbname: 'test'
        user: 'test'
        host: 'localhost'
        password: 'test'

and test::

    ---
    variables:
        data_id: '{{ random(1) }}'  # random positive int
    steps:
        - http:
            post:
              url: '{{ data_service_url }}'
              body: {key: '{{ data_id }}', data: 'foo'}
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              sql: 'select * from test where id={{ data_id }};'

Here we used `data_service_url` and `postgres_conf` variables, defined in the `test_inventory` and
`data_id` defined in test. We can also register variables on the fly, which is extremely useful for
data checks.

Register variables
------------------
Imagine we have a table **test**:

+---------+-------------+
|   id    |    value    |
+============+==========+
|  int    | varchar[255]|
+---------+-------------+

Let's register postgres read result and compare it with expected one::

    ---
    variables:
        data_id: 1
    steps:
        - http:
            post:
              url: '{{ data_service_url }}/api/v1/test'
              body: {key: '{{ data_id }}', data: 'foo'}
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              sql: 'select * from test where id={{ data_id }};'
            register: {document: '{{ OUTPUT }}'}
        - check:
            equals: {the: '{{ document.value }}', is: 'foo'}

Here we've registered the whole output of postgres query command into the `document` variable and
access it in `check` step later. In `check equals` step we access `value` column, which has `foo` value.
With `register` step you can register part of output::

    # same steps as below
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              sql: 'select * from test where id={{ data_id }};'
            register: {foo: '{{ OUTPUT.value }}'}
        - check:
            equals: {the: '{{ foo }}', is: 'foo'}

and you can also register multiple variables::

    # same steps as below
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              sql: 'select * from test where id={{ data_id }};'
            register: {foo: '{{ OUTPUT.value }}', id: '{{ OUTPUT.id }}'}
        - check:
            equals:
              and:
                - {the: '{{ foo }}', is: 'foo'}
                - {the: '{{ id }}', is: '{{ data_id }}'}

Compact same steps
------------------
You can compact similar steps in one with `actions`::

    ---
    steps:
      - postgres:
          request:
            conf: '{{ pg_conf }}'
            sql: 'insert into test(id, num) values({{ id }}, {{ num }});'
      - postgres:
          request:
            conf: '{{ pg_conf }}'
            sql: 'select * from test where id={{ id }};'
          register: {document: '{{ OUTPUT }}'}

to::

    ---
    steps:
      - postgres:
          actions:
            - request:
                conf: '{{ pg_conf }}'
                sql: 'insert into test(id, num) values({{ id }}, {{ num }});'
            - request:
                conf: '{{ pg_conf }}'
                sql: 'select * from test where id={{ id }};'
              register: {document: '{{ OUTPUT }}'}

Name your steps
---------------
When you run your test you will see something like this::

    INFO:catcher:Step echo OK
    INFO:catcher:Step postgres OK
    INFO:catcher:Step postgres OK
    INFO:catcher:Step check OK

Which is not so useful if you have lots of steps. Name them::

    ---
    variables:
        data_id: 1
    steps:
        - http:
            post:
              url: '{{ data_service_url }}'
              body: {key: '{{ data_id }}', data: 'foo'}
            name: 'load data to service {{ data_service_url }}'
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              sql: 'select * from test where id={{ data_id }};'
            register: {document: '{{ OUTPUT }}'}
            name: 'check data in postgres'
        - check:
            equals: {the: '{{ document.value }}', is: 'foo'}
            name: 'check data equality'

And you will see::

    INFO:catcher:Step load data to service 127.0.0.1/save_data OK
    INFO:catcher:Step check data in postgres OK
    INFO:catcher:Step check data equality OK

Ignore errors
-------------
You can ignore a step's errors and continue the test::

    ---
    steps:
      - postgres:
          actions:
            - request:
                conf: '{{ pg_conf }}'
                sql: 'create table test(id serial PRIMARY KEY, num integer);'
              ignore_errors: true
            - request:
                conf: '{{ pg_conf }}'
                sql: 'insert into test(id, num) values({{ id }}, {{ num }});'
            - request:
                conf: '{{ pg_conf }}'
                sql: 'select * from test where id={{ id }}'
              register: {document: '{{ OUTPUT }}'}

It is extremely useful, when you need to wait for some resource to be initialised::

    loop:
      name: 'Wait for postgres to be ready'
      while:
        if: '{{ ready != 1 }}'
        do:
        - wait: {seconds: 1}
        - postgres:
            name: 'check db'
            request:
              conf: '{{ postgres_conf }}'
              sql: "select 1"
            ignore_errors: true
            register: {ready: '{{ OUTPUT }}'}
        max_cycle: 120  # 2 minutes

New in `1.17.0` - you can now use `Wait.for` instead::

    ---
    steps:
        - wait:
            seconds: 30
            for:
                postgres:
                    request:
                        conf: '{{ postgres_conf }}'
                        sql: 'select 1;'
        - other_steps

In this case `other_steps` will be executed only when `select 1;` becomes true. Test will fail after 30 seconds,
if `select 1;` is still failing.

Skip steps
----------
| You can skip your steps based on conditions.
| Imagine you have 2 services under one API (new and legacy). If user is registered via Facebook Oauth2 - his loan is
  stored in Postgres.
| For legacy users with credentials based registration loans are stored in Couchbase.
| In your test you need to create loan for the test user, but you may not know which database you should populate.
Example::

    steps:
        - http:
            get:
                url: '{{ my_web_service }}/api/v1/users?id={{ user_id }}'
            register: {registration_type: '{{ OUTPUT.data.registration }}'}
            name: 'Determine registration type for user {{ user_id }}'
        - postgres:
            request:
                conf: 'test:test@localhost:5433/test'
                sql: "insert into loans(value) values(1000) where user_id == '{{ user_id }}';"
            name: 'Update user loan for facebook user'
            skip_if:
                equals: {the: '{{ registration_type }}', is_not: 'facebook'}
        - couchbase:
            request:
                conf:
                    bucket: loans
                    host: localhost
                put:
                    key: '{{ user_id }}'
                    value: {value: 1000}
            skip_if:
                equals: {the: '{{ registration_type }}', is_not: 'other'}
            name: 'Update user loan for legacy user'

In this example step postgres is skipped for legacy users and step couchbase is skipped for new users.

You can use any :meth:`catcher.steps.check` in skip_if condition.

Short form::

    variables:
        no_output: true
    steps:
        - echo:
            from: '{{ my_data }}'
            skip_if: '{{ no_output }}'

Is same as::

        - echo:
            from: '{{ my_data }}'
            skip_if:
                equals: {the: '{{ no_output }}', is: true}

Multiple clauses::

    variables:
        services: {'service1: 'provided', 'service2': 'runtime']
        in_docker: true
    steps:
        - sh:
            command: "grep 'docker|lxc' /proc/1/cgroup"
            return_code: 1
            ignore_errors: true
            register: {in_docker: false}
        - docker:
            start:
                image: 'my_service1_image'
                ports:
                    '1080/tcp': 8000
            skip_if:
                or:
                    - equals: {the: '{{ services.service1 }}', is: 'provided'}
                    - equals: {the: '{{ in_docker }}', is: true}

Will start `my_service1_image` in docker if current test is not running in docker and service1 is not provided.

Do a cleanup
------------

If your steps modify data you can do a clean up. Use `finally` block the same way you are using `steps`. You can also
add **run_if** parameter to steps to specify when clean up steps should be run: **'always'** will always run, it is the
default value, **'pass'** will run only if test passes, **'fail'** will run only if test fails.

Run test, do a cleanup, if test passes - notify google chat. ::

    steps:
        - http:
            get:
                url: '{{ my_web_service }}/api/v1/users?id={{ user_id }}'
            register: {registration_type: '{{ OUTPUT.data.registration }}'}
            name: 'Determine registration type for user {{ user_id }}'
        - postgres:
            request:
                conf: '{{ postgres_conf }}'
                sql: "insert into loans(value) values(1000) where user_id == '{{ user_id }}';"
            name: 'Update user loan for facebook user'
    finally:
        - postgres:
            request:
                conf: '{{ postgres_conf }}'
                sql: "delete from loans(value) where user_id == '{{ user_id }}';"
            name: 'Clean up user'
        - http:
            post:
                url: '{{ google_chat_webhook_url }}'
                headers: {Content-Type: 'application/json'}
                data: {text: 'Test passed. You can deploy the service now'}
            run_if: 'pass'


Ignore the test
---------------

Sometimes some tests are broken and you don't have time to fix them. Or you have test which run in your cloud environment,
but not locally. Just ignore them!

Simple ignore::

    ignore: true  # this test is failing for some reason
    variables:
        foo: bar
    steps:
        - check: {equals: {the: true, is: false}}

Ignore based on os env var::

    ignore:
        equals: {the: '{{ CLOUD }}', is_not: 'AWS'}
    variables:
        foo: bar
    steps:
        - check: {equals: {the: true, is: false}}

Run test everywhere except local inventory::

    ignore:
        equals: {the: '{{ INVENTORY }}', is: 'local'}
    variables:
        foo: bar
    steps:
        - check: {equals: {the: true, is: false}}
