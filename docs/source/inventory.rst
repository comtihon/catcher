Inventories
===========

| Inventory file is a file where you set up most common variables, like hosts, credentials and urls.
| You can run your tests without inventories, but they are recommended if you have multiple environments to test.

Example
-------

Here is `dev_inventory.yaml`::

    ---
    kafka_server: 'kafka.dev.host.de'
    deposit_admin_topic: 'admin_service.deposits'
    bank_admin_service: 'http://bank_admin.dev.host.de'
    admin_user: 'Admin'
    admin_pass: 'qwerty'

And here is the test using it::


    ---
    steps:
        - http:
            actions:
              - post:
                  url: '{{ bank_admin_service }}/login'
                  body: {user: '{{ admin_user }}', pass: ' {{ admin_pass }}'}
                register: {token: '{{ OUTPUT.token }}'}
              - post: # set auto deposit for all new users
                  url: '{{ bank_admin_service }}/set_initial_deposit'
                  headers: {token: '{{ token }}'}
                  body: {data: '{{ deposit }}', currency: 'EUR'}
                register: {order_id: '{{ OUTPUT.data.id }}'}
        - wait: {seconds: 0.5}
        - kafka:
            produce:  # approve auto deposit (mocks external service)
              server: '{{ kafka_server }}'
              topic: '{{ deposit_admin_topic }}'
              data: {id: '{{ order_id }}', action: 'APPROVED'}

To run test with specified inventory use `-i` parameter: `catcher -i inventory/dev_inventory.yaml tests`

Different formats
-----------------
You may noticed that sometimes the same step's configuration can have different formats.
See this inventory file as an example::

        postgres_str: 'test:test@localhost:5433/test'
        postgres_str_obj:
            url: 'test:test@localhost:5433/test'
            type: postgres
        postgres_obj:
            dbname: 'test'
            user: 'test'
            password: 'test'
            host: 'localhost'
            port: 5433
            type: 'postgres'

It contains 3 postgres database configurations in different formats.

The first one is a nice short form. It contains all configuration in a single line and can be used only in
`Postgres <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher-modules-database-postgres-module>`_ step.

The second is Airflow-compatible short form. It has the same short form moved to **url** param, and with additional
**type** param. Such configuration can be used both in Postgres and
`Airflow <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.pipeline.html#catcher-modules-pipeline-airflow-module>`_ step.
If you found out, that Airflow is working with this conf, but not with your step, try ``{{ postgres_str_obj.url }}``
in your step (and create a github issue).

The fird one is an object configuration. It is a bit longer, but the nice thing is - you can access any part of it in the test:
``{{ postgres_obj.user }}``. If **type** is specified - it is compatible with Airflow.

Airflow compatibility
^^^^^^^^^^^^^^^^^^^^^
By Airflow compatibility I mean that the same configuration from the **inventory** file can be used by both normal steps, which
are using this configuration directly and by Airflow step, which will take this config from inventory file and put into the airflow connection.
If you don't know what Airflow is or you are not testing it - you can ignore this and just use short form (first option) or object form (third option).