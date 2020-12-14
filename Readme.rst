.. image:: https://travis-ci.com/comtihon/catcher.svg?branch=master
    :target: https://travis-ci.org/comtihon/catcher
.. image:: https://img.shields.io/pypi/v/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://img.shields.io/pypi/pyversions/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://img.shields.io/pypi/wheel/catcher.svg
    :target: https://pypi.python.org/pypi/catcher
.. image:: https://patrolavia.github.io/telegram-badge/chat.png
    :target: https://t.me/catcher_e2e

Microservices automated test tool
=================================
Support your team with a good Catcher!

.. image:: https://raw.githubusercontent.com/comtihon/catcher/master/docs/_static/logo_big.png
   :scale: 50 %

What is catcher?
----------------
Catcher is a flexible end to end test tool, that can be used for automated microservices or data pipelines testing.
It helps you to check either one service or whole system interaction from the front-end to the back-end.
With the help of Catcher you can easily mock external services your system relies on. Catcher is not about only http, it
can check different services, such as Kafka, Postgres, CouchBase, Mongodb, Elastic, S3, emails and others.

Quickstart and documentation
----------------------------
1. Check, how to write a `test <https://catcher-test-tool.readthedocs.io/en/latest/source/tests.html>`_.
2. Get to know how to `install <https://catcher-test-tool.readthedocs.io/en/latest/source/run.html>`_ and run Catcher.
3. List all `steps <https://catcher-test-tool.readthedocs.io/en/latest/source/steps.html>`_ and select those you need.
4. Learn more about `variables <https://catcher-test-tool.readthedocs.io/en/latest/source/variables.html>`_ and `resources <https://catcher-test-tool.readthedocs.io/en/latest/source/resources.html>`_
5. Read how to trace and debug your test using `reports <https://catcher-test-tool.readthedocs.io/en/latest/source/reports.html>`_

For more information check `readthedocs`_.

Very quick start
----------------
You can run Catcher in `docker`_ with all libraries, drivers and steps already installed and configured. It allows
you to try Catcher without installing anything.

Just run the minimal command::

    docker run -v $(pwd)/inventory:/opt/catcher/inventory
               -v $(pwd)/tests:/opt/catcher/tests
                catcher -i inventory/my_inventory.yml tests

It will ask Catcher to run everything within your local **tests** folder using **inventory/my_inventory.yml**. For more
information please check run `instructions <https://catcher-test-tool.readthedocs.io/en/latest/source/run.html>`_

.. _docker: https://hub.docker.com/repository/docker/comtihon/catcher

How does it look like?
----------------------

Imagine you have a **user_service** which saves users in **postgre** and posts them to **kafka** topic, where they are
consumed by another service, which sends them emails.
You mention your environment in the inventory files.

local.yml::

    kafka_server: '127.0.0.1:9092'
    postgres: 'test:test@localhost:5433/test'
    user_service: 'http://127.0.0.1:9090'
    email_config:
        host: '127.0.0.1:12345'
        user: 'local_user'
        pass: 'local_pass'

develop.yml::

    kafka_server: 'kafka.dev.mycompany.com:9092'
    postgres: 'dev:dev@postgres.dev.mycompany.com:5433/test'
    user_service: 'http://user_service.dev.mycompany.com:9090'
    email_config:
        host: 'imap.google.com'
        user: 'my_user@google.com'
        pass: 'my_pass'

You write a test::

    variables: # here you specify test-local variables
        users:
            - email: '{{ test_user@my_company.com }}'
              name: '{{ random("name") }}' # templates fully supported
            - email: '{{ random("email") }}'
              name: '{{ random("name") }}'
    steps: # here you write steps which Catcher executed one by one until it fails
        - http:
            post:
                url: '{{ user_service }}/sign_up' # user_service value is taken from active inventory which you specify at runtime
                body: '{{ users[0] }}' # send first user from variables as a POST body
                headers: {Content-Type: 'application/json'}
                response_code: 2xx # will accept 200-299 codes
            name: 'Register {{ users[0].email }} as a new user' # name your step properly (Optional)
            register: {user_id: '{{ OUTPUT.id }}'}  # register new variable user_id as id param from json response
        - postgres: # check if user was saved in the database
            request:
                conf: '{{ postgres }}'
                sql: 'select * from users where user_id = {{ user_id }}'  # user_id from previous step will be used in this template
            register: {email_in_db: '{{ OUTPUT.email }}'}  # load full user data and register only email as a new variable
        - check: # compare email from the database with real user email
            equals: {the: '{{ users[0].email }}', is: '{{ email_id_db }}'}}  # checks the equality between two strings. Templates supported.
        - kafka:
            consume:  # check if user_service pushed newly created user to kafka
                server: '{{ kafka_server }}' # kafka_server value is taken from active inventory
                topic: 'new_users'
                where: # filter all messages except messages for our user
                    equals: {the: '{{ MESSAGE.user_id }}', is: '{{ user_id }}'}
        - email: # check if email was sent for this user
              receive:
                  config: '{{ email_conf }}'
                  filter: {unread: true, subject: 'Welcome {{ users[0].name }}'} # select all unread and filter by subject
                  ack: true  # mark as read
                  limit: 1
              register: {messages: '{{ OUTPUT }}'}  # register all messages found (0 or 1)
        - check: '{{ messages |length > 0 }}' # short form of compare - we should have more than 0 messages co pass this step
    finally:
        - postgres: # delete user from database to cleanup after test finishes (no matter successfully or not)
            request:
                conf: '{{ postgres }}'
                sql: 'delete from users where user_id = {{ user_id }}'

For local environment run it as::

    catcher -i inventories/local.yml tests/my_test.yml

For dev::

    catcher -i inventories/develop.yml tests/my_test.yml

See `microservices`_ for more complex example.

Customization
-------------
Catcher can be easily customized to serve your needs.

1. You can write your own functions and filters and use them in your step's `templates <https://catcher-test-tool.readthedocs.io/en/latest/source/filters_and_functions.html>`_.
2. You can create your own `modules <https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html>`_ (in Python, Java, Kotlin, JS, jar-files or any executable)
3. You can write your steps in catcher itself and `include <https://catcher-test-tool.readthedocs.io/en/latest/source/includes.html#run-on-action>`_ them from other tests.

Why catcher?
------------

* don't repeat test code. Write one test and call its steps from another;
* compute and override variables to check your data and compose new flexible requests;
* write test for development, change inventory and test stage/uat/prod with no changes;
* test your data pipelines with `Airflow <https://catcher-modules.readthedocs.io/en/latest/source/airflow.html>`_ step;
* test your front-end <-> back-end integration with `Selenium <https://catcher-modules.readthedocs.io/en/latest/source/selenium.html>`_ step;
* test all your `microservices`_ with ease;
* `modular`_ architecture
* bulk-prepare and bulk-check data for you tests with `prepare-expect`_ step
* automate your testing!

Changelog is `here <https://github.com/comtihon/catcher/blob/master/Changelog.rst>`_.

Contributors:
-------------
* Many thanks to `Ekaterina Belova <https://github.com/kbelova>`_ for core & modules contribution.

.. _readthedocs: https://catcher-test-tool.readthedocs.io/en/latest/
.. _microservices: https://catcher-test-tool.readthedocs.io/en/latest/source/microservices.html
.. _modular: https://catcher-test-tool.readthedocs.io/en/latest/source/modules.html
.. _prepare-expect: https://catcher-modules.readthedocs.io/en/latest/source/prepare_expect.html
.. _selenium: https://catcher-modules.readthedocs.io/en/latest/source/selenium.html