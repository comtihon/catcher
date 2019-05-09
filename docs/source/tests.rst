How to write a test
===================
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
              query: 'select * from test where id=1'

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
        data_id: 1
    steps:
        - http:
            post:
              url: '{{ data_service_url }}'
              body: {key: '{{ data_id }}', data: 'foo'}
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              query: 'select * from test where id={{ data_id }};'

Here we used `data_service_url` and `postgres_conf` variables, defined in the `test_inventory` and
`data_id` defined in test. We can also register variables on the fly, which is extremely useful for
data checks.

Register variables
------------------
Let's register postgres read result and compare it with expected one::

    ---
    variables:
        data_id: 1
    steps:
        - http:
            post:
              url: '{{ data_service_url }}'
              body: {key: '{{ data_id }}', data: 'foo'}
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              query: 'select * from test where id={{ data_id }};'
            register: {document: '{{ OUTPUT }}'}
        - check:
            equals: {the: '{{ document[1] }}', is: 'foo'}

Here we've registered the whole output of postgres query command into the `document` variable and
access it in `check` step later. In `check equals` step we access second column, which has `foo` value (first one is id).
With `register` step you can register part of output::

    # same steps as below
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              query: 'select * from test where id={{ data_id }};'
            register: {foo: '{{ OUTPUT }}[1]'}
        - check:
            equals: {the: '{{ foo }}', is: 'foo'}

and you can also register multiple variables::

    # same steps as below
        - postgres:
            request:
              conf: '{{ postgres_conf }}'
              query: 'select * from test where id={{ data_id }};'
            register: {foo: '{{ OUTPUT }}[1]', id: '{{ OUTPUT }}[0]'}
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
            query: 'insert into test(id, num) values({{ id }}, {{ num }});'
      - postgres:
          request:
            conf: '{{ pg_conf }}'
            query: 'select * from test where id={{ id }};'
          register: {document: '{{ OUTPUT }}'}

to::

    ---
    steps:
      - postgres:
          actions:
            - request:
                conf: '{{ pg_conf }}'
                query: 'insert into test(id, num) values({{ id }}, {{ num }});'
            - request:
                conf: '{{ pg_conf }}'
                query: 'select * from test where id={{ id }};'
              register: {document: '{{ OUTPUT }}'}

Ignore errors
-------------
You can ignore a step's errors and continue the test::

    ---
    steps:
      - postgres:
          actions:
            - request:
                conf: '{{ pg_conf }}'
                query: 'create table test(id serial PRIMARY KEY, num integer);'
              ignore_errors: true
            - request:
                conf: '{{ pg_conf }}'
                query: 'insert into test(id, num) values({{ id }}, {{ num }});'
            - request:
                conf: '{{ pg_conf }}'
                query: 'select * from test where id={{ id }}'
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
              query: "select 1"
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
                        query: 'select 1;'
        - other_steps

 In this case `other_steps` will be executed only when `select 1;` is true or after 30 seconds.

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
              query: 'select * from test where id={{ data_id }};'
            register: {document: '{{ OUTPUT }}'}
            name: 'check data in postgres'
        - check:
            equals: {the: '{{ document[1] }}', is: 'foo'}
            name: 'check data equality'

And you will see::

    INFO:catcher:Step load data to service 127.0.0.1/save_data OK
    INFO:catcher:Step check data in postgres OK
    INFO:catcher:Step check data equality OK

