Resources
=========

Usage
-----
Resources can be used in different steps during the tests.
**resources/data/user.json**::

    {
        "email": "my_user@test.de",
        "firstName": "John",
        "lastName": "Doe",
        ...some other fields...
    }


:meth:`catcher.modules.steps.http` step can take prepared body from file::

        http:
          post:
            url: 'http://test.com'
            body_from_file: "data/user.json"

Which is much better, than store a lot of data in the test itself. Resources can be shared between tests.

Templates in resources
----------------------
Sharing static resources between tests is not that useful. That's why resources fully support templates.
You can use any placeholder to pass your variable from test's variables to the resource.
**resources/messages/user_message.json** ::

    {
        "email": "{{ user_email }}",
        "firstName": "{{ firstName }}",
        "lastName": "{{ lastName }}"
    }

And then use it in your `rabbit <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.mq.html#catcher-modules-mq-rabbit-module>`_ step::

    rabbit:
        publish:
            config: '{{ rabbitmq_config }}''
            exchange: 'test.catcher.exchange'
            routing_key: 'catcher.routing.key'
            data_from_file: 'messages/user_message.json'

Advanced templating
-------------------
Templating is not only about putting values in the placeholders. You can even generate data. Imagine you need a csv file
for the `prepare <https://catcher-modules.readthedocs.io/en/latest/source/prepare_expect.html>`_ step to populate your
database before tests with all the users.
**resources/data/users.csv**::

    user_id,email
    {%- for user in users %}
    {{ user.uuid }},{{ user.email }}
    {%- endfor -%}

Here we used Jinja2 for-loop to create a row in your csv file for every user in your `users` variable.
In the test it will look like::

    ---
    variables:
      users:
        - uuid: '{{ random("uuid4") }}'
          email: '{{ random("email") }}'
        - uuid: '{{ random("uuid4") }}'
          email: '{{ random("email") }}'
        - uuid: '{{ random("uuid4") }}'
          email: '{{ random("email") }}'
    steps:
      - prepare:
          populate:
            mysql:
              conf: '{{ mysql_conf }}'
              schema: my_table.sql
              data:
                my_table: data/users.csv
          name: 'Create table and populate initial data'

Source compilation
------------------
If you are using your own steps, written in other languages needed to be compiled first (Java/Kotlin/...) you can also
put the source file in the resources directory.
Imagine you are using `Selenium <https://catcher-modules.readthedocs.io/en/latest/source/selenium.html>`_ step for
front-end testing. The Selenium part you write in Java and put the source in the `resources/front_end/MyTest.java`. Then
you can call it from Catcher::

    - selenium:
        test:
            file: front_end/MyTest.java
            libraries: '/usr/share/java/*'

Catcher will:

- go to resources and find your **MyTest.java** source file
- inject templates there (if any)
- compile and run it.

Docker compose
--------------
If you put file named `docker-compose.yml` file in resources - Catcher will automatically run it before running all tests and stop
afterwards.