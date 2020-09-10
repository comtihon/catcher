Internal modules
================
Internal modules are part of catcher-core package. They become available as soon as you install catcher.

check - collection of different checks
--------------------------------------

.. automodule:: catcher.steps.check
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: action, Operator, Check

echo - write data to stdout or file
-----------------------------------

.. autoclass:: catcher.steps.echo.Echo
    :members:
    :noindex:
    :exclude-members: action

loop - loop over the data
-------------------------

.. autoclass:: catcher.steps.loop.Loop
    :members:
    :noindex:
    :exclude-members: action

http - perform http request
---------------------------

.. autoclass:: catcher.steps.http.Http
    :members:
    :noindex:
    :exclude-members: action

sh - run shell command
----------------------

.. autoclass:: catcher.steps.sh_step.Sh
    :members:
    :noindex:
    :exclude-members: action

run another testcase
--------------------

.. autoclass:: catcher.steps.run.Run
    :members:
    :noindex:
    :exclude-members: action

stop - stop testcase execution
------------------------------

.. autoclass:: catcher.steps.stop.Stop
    :members:
    :noindex:
    :exclude-members: action

wait - delay testcase execution
-------------------------------

.. autoclass:: catcher.steps.wait.Wait
    :members:
    :noindex:
    :exclude-members: action

External modules
================
External modules are a part of catcher-modules package. Each of them should be installed separately. Every module could
have it's own dependencies and libraries.

redis - works with redis cache
------------------------------
Put value to `Redis <https://redis.io/>`_ cache or get it, increment/decrement or delete::

    Decrement, increment by 5 and delete
    ::

        - redis:
            request:
                set:
                    'foo': 11
        - redis:
            request:
                decr: baz
        - redis:
            request:
                incrby:
                    foo: 5
        - redis:
            request:
                delete:
                    - baz


Get value by key 'key' and register in variable 'var'::

    redis:
      request:
        get: 'key'
      register: {var: '{{ OUTPUT }}'}

For the full documentation see catcher-modules `Redis <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.cache.html#catcher-modules-cache-redis-module>`_.

couchbase - works with couchbase nosql database
-----------------------------------------------
Allows you to perform put/get/delete/query operations in `Couchbase <https://www.couchbase.com/>`_::

    couchbase:
      request:
        conf:
            bucket: test
            user: test
            password: test
            host: localhost
        query: "select `baz` from test where `foo` = 'bar'"

For the full documentation see catcher-modules `Couchbase <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher_modules.database.couchbase.Couchbase>`_.

**Dependencies**:

* libcouchbase library is required to run this step.

postgres - works with postgres sql database
-------------------------------------------
Allows you to run sql queries in `Postgres <https://www.postgresql.org/>`_. Supports both string and object configuration.
Execute ddl resource **resources/my_script.sql**::

    postgres:
      request:
        conf: 'postgresql://user:password@localhost:5432/test'
        sql: 'my_script.sql'


Fetch document and check if it's id is equal to **num** variable::

    - postgres:
        request:
            conf:
                dbname: test
                user: user
                password: password
                host: localhost
                port: 5433
            sql: select * from test where id={{ id }}
        register: {document: '{{ OUTPUT }}'}
    - check:
        equals: {the: '{{ document.id }}', is: '{{ num }}'}

For the full documentation see catcher-modules `Postgres <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher-modules-database-postgres-module>`_.

mongo - works with mongodb nosql database
-----------------------------------------
Allows you to run different commands in `MongoDB <https://www.mongodb.com/>`_
Find one post for author `Mike` and register it as a **document** variable::

    mongo:
        request:
            conf: 'mongodb://username:password@host'
            collection: 'your_collection'
            find_one: {'author': 'Mike'}
        register: {document: '{{ OUTPUT }}'}

Chain operations `db.collection.find().sort().count()` to find all posts of author `Mike`, sort them by title and count::

    mongo:
        request:
            conf: 'mongodb://username:password@host'
            collection: 'your_collection'
            find: {'author': 'Mike'}
            next:
              sort: 'title'
              next: 'count'

For the full documentation see catcher-modules `Mongo <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher_modules.database.mongo.Mongo>`_.

oracle - works with oracle sql database
---------------------------------------
Allows you to run sql queries in `OracleDB <https://www.oracle.com/database/>`_. Supports both string and object configuration.
Insert into **test** table one row::

    oracle:
        request:
            conf: 'user:password@localhost:1521/test'
            sql: 'insert into test(id, num) values(3, 3);'

For the full documentation see catcher-modules `Oracle <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher_modules.database.oracle.Oracle>`_.

**Dependencies**:

* `libclntsh.dylib` is required for `oracle`. Read more `here <https://oracle.github.io/odpi/doc/installation.html>`_.


sqlite - works with sqlite sql embedded database
------------------------------------------------
Allows you to create `SQLite <https://www.sqlite.org/index.html>`_ database on your local filesystem and work with it.
Supports both string and object configuration.

**Important** - for relative path use one slash `/`. For absolute slash - two `//`.
Select all from test, use relative path::

    sqlite:
      request:
          conf: '/foo.db'
          sql: 'select count(*) as count from test'
      register: {documents: '{{ OUTPUT }}'}

Insert into test, using absolute path (with 2 slashes)::

    sqlite:
      request:
          conf: '//absolute/path/to/foo.db'
          sql: 'insert into test(id, num) values(3, 3);'

For the full documentation see catcher-modules `SQLite <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher_modules.database.sqlite.SQLite>`_.

mysql - works with mysql sql database
-------------------------------------
Allows you to run queries on `MySQL <https://www.mysql.com/>`_ (and all mysql compatible databases like `MariaDB <https://mariadb.org/>`_).
Supports both string and object configuration.
Insert one row in **test** table::

    mysql:
      request:
          conf: 'user:password@localhost:3306/test'
          sql: 'insert into test(id, num) values({{ id }}, {{ num }});'

For the full documentation see catcher-modules `MySQL <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher-modules-database-mysql-module>`_.

mssql - works with mssql sql database
-------------------------------------
Allows you to run queries on Microsoft SQL `Server <https://www.microsoft.com/en-us/sql-server/>`_.
Supports both string and object configuration.
Count all rows in test, specify driver manually::

    mssql:
      request:
          conf:
              dbname: test
              user: user
              password: password
              host: localhost
              port: 1433
              driver: ODBC Driver 17 for SQL Server
          sql: 'select count(*) as count from test'
      register: {documents: '{{ OUTPUT }}'}

Insert row in **test** table. Use default **ODBC Driver 17 for SQL Server** driver name::

    mssql:
      request:
          conf: 'user:password@localhost:5432/test'
          sql: 'insert into test(id, num) values(3, 3);'

Use `pymssql <https://pypi.org/project/pymssql/>`_ library instead of odbc driver::

    mssql:
      request:
          conf: 'mssql+pymssql://user:password@localhost:5432/test'
          sql: 'insert into test(id, num) values(3, 3);'

**Dependencies**:

* mssql driver is required for `mssql`. Read more `here <https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server>`_.

For the full documentation see catcher-modules `MSSQL <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.database.html#catcher-modules-database-mssql-module>`_.

selenium - run prepared selenium test for front-end testing
-----------------------------------------------------------
This complex step consists of two parts. First - you need to create a `Selenium <https://www.selenium.dev/>`_ script and put it in the Catcher's resources directory.
Second - run the step in Catcher.

Catcher variables can be accessed from Selenium script via environment variables. All output from Selenium script is routed
to Catcher **OUTPUT** variable.

If you specify java/kotlin source file as a Selenium script - Catcher will try to compile it using system's compiler.

Use geckodriver to run python-selenium test **my_test.py** from resources directory::

    - selenium:
        test:
            driver: '/opt/bin/geckodriver'
            file: 'my_test.py'

You can read more information on Catcher and Selenium integration in separate `document <https://catcher-modules.readthedocs.io/en/latest/source/selenium.html>`_

**Dependencies**:

* Selenium browser `drivers <https://www.selenium.dev/documentation/en/webdriver/driver_requirements/>`_
* Selenium client `libraries <https://www.selenium.dev/documentation/en/selenium_installation/installing_selenium_libraries>`_
* `NodeJS <https://nodejs.org/en/>`_ for running JS Selenium steps
* `Java <https://www.java.com/en/download/>`_ for running all Jar-precompiled Selenium steps
* `JDK <https://jdk.java.net/>`_ if you wish to compile Java source code
* `Kotlin <https://kotlinlang.org/>`_ compiler if you wish to compile Kotlin source code

For the module documentation see catcher-modules `Selenium <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.frontend.html#catcher_modules.frontend.selenium.Selenium>`_.

marketo - interact with Adobe Marketo marketing automation tool
---------------------------------------------------------------
Allows you to read/write/delete leads in Adobe `Marketo <https://www.marketo.com>`_ marketing automation tool.

Read **id**, **email** and **custom_field_1** fields from lead found by **custom_id** field having `my_value_1` or `my_value_2` values::

    marketo:
        read:
            conf:
                munchkin_id: '{{ marketo_munchkin_id }}'
                client_id: '{{ marketo_client_id }}'
                client_secret: '{{ marketo_client_secret }}'
            fields: ['id', 'email', 'custom_field_1']
            filter_key: 'custom_id'
            filter_value: ['my_value_1', 'my_value_2']
        register: {leads: '{{ OUTPUT }}'}

Update leads by **custom_id** field::

    marketo:
        write:
            conf:
                munchkin_id: '{{ marketo_munchkin_id }}'
                client_id: '{{ marketo_client_id }}'
                client_secret: '{{ marketo_client_secret }}'
            action: 'updateOnly'
            lookupField: 'custom_id'
            leads:
                - custom_id: 14
                  email: 'foo@bar.baz'
                  custom_field_1: 'some value'
                - custom_id: 15
                  email: 'foo2@bar.baz'
                  custom_field_1: 'some other value'

For the module documentation see catcher-modules `Marketo <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.marketing.html#catcher-modules-marketing-marketo-module>`_.

kafka - consume/produce in the kafka message queue
--------------------------------------------------
Allows you to consume/produce messages from/to Apache `Kafka <https://kafka.apache.org/>`_

Read message from **test_consume_with_timestamp** topic with **timestamp** field > 1000::

    kafka:
        consume:
            server: '127.0.0.1:9092'
            group_id: 'test'
            topic: 'test_consume_with_timestamp'
            timeout: {seconds: 5}
            where:
                equals: '{{ MESSAGE.timestamp > 1000 }}'

Produce **data** variable as json message to the topic **test_produce_json**::

    kafka:
        produce:
            server: '127.0.0.1:9092'
            topic: 'test_produce_json'
            data: '{{ data|tojson }}'

For the module documentation see catcher-modules `Kafka <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.mq.html#catcher-modules-mq-kafka-module>`_.

rabbit - consume/produce in the rabbit message queue
----------------------------------------------------
Allows you to consume/produce messages from/to `RabbitMQ <https://www.rabbitmq.com/>`_

Publish **resources/path/to/file.json** file to the **test.catcher.exchange** exchange::

    rabbit:
        publish:
            config:
                server: 127.0.0.1:5672
                username: 'guest'
                password: 'guest'
            exchange: 'test.catcher.exchange'
            routing_key: 'catcher.routing.key'
            data_from_file: '{{ path/to/file.json }}'

Consume message from **my_queue** and register it as a **message** variable. Configuration is stored in variable::

    rabbit:
        consume:
            config: '{{ rabbit_conf }}'
            queue: 'my_queue'
        register: {message: '{{ OUTPUT }}'}

For the module documentation see catcher-modules `Rabbit <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.mq.html#catcher-modules-mq-rabbit-module>`_.

docker - interact with docker containers
----------------------------------------
Allows you to start/stop/disconnect/connect/exec commands, get logs and statuses of `Docker <https://www.docker.com/>`_ containers.
Is very useful when you need to run something like `Mockserver <https://www.mock-server.com/>`_ and/or simulate network disconnects.

Run blocking command `echo hello world` in a new **alpine** container. Register output as a **logs** variable::

    docker:
        start:
            image: 'alpine'
            cmd: 'echo hello world'
            detached: false
        register: {logs: '{{ OUTPUT.strip() }}'}

Start named container detached with volumes and environment::

    docker:
        start:
            image: 'my-backend-service'
            name: 'mock server'
            ports:
                '1080/tcp': 8000
            environment:
                POOL_SIZE: 20
                OTHER_URL: {{ service1.url }}
            volumes:
                '{{ CURRENT_DIR }}/data': '/data'
                '/tmp/logs': '/var/log/service'

For the module documentation see catcher-modules `Docker <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.service.html#catcher-modules-service-docker-module>`_.

elastic - run queries on elasticsearch
--------------------------------------
Allows you to get data from `Elasticsearch <https://www.elastic.co/elastic-stack>`_. Useful, when your services push their
logs there and you need to check the logs automatically from the test.

Get only field **name** of all documents containing `three` in the **payload**, register as **doc** variable::

    elastic:
        search:
            url: 'http://127.0.0.1:9200'
            index: test
            query:
                match: {payload : "three"}
            _source: ['name']
        register: {doc: '{{ OUTPUT }}'}

Get all documents which has `round` **shape** and `red` or `blue` **color**, register as **doc** variable::

    elastic:
        search:
            url: 'http://127.0.0.1:9200'
            index: test
            query:
                bool:
                    must:
                        - term: {shape: "round"}
                        - bool:
                            should:
                                - term: {color: "red"}
                                - term: {color": "blue"}
        register: {doc: '{{ OUTPUT }}'}

For the module documentation see catcher-modules `Elastic <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.service.html#catcher-modules-service-elastic-module>`_.

s3 - work with files in aws s3
------------------------------
Allows you to get/put/list/delete files in `Amazon S3 <https://aws.amazon.com/s3/>`_

Useful hint: for local testing you can use `Minio <https://min.io/>`_ run in docker as it is S3 API compatible.

Put file **resources/my_file** as **/foo/file.txt**::

    s3:
        put:
            config:
                url: http://127.0.0.1:9001
                key_id: minio
                secret_key: minio123
            path: /foo/file.txt
            content_resource: 'my_file'

Put variable **content** as a file **/foo/file.txt**::

    s3:
        put:
            config: '{{ s3_config }}'
            path: /foo/file.txt
            content: '{{ content }}'

Get file **/foo/baz/bar/file.txt** from S3 and put it in **data** variable::

    s3:
        get:
            config: '{{ s3_config }}'
            path: /foo/baz/bar/file.txt
        register: {data: '{{ OUTPUT }}'}

For the module documentation see catcher-modules `S3 <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.service.html#catcher-modules-service-s3-module>`_.

prepare - allows you to generate and push data to the database
--------------------------------------------------------------
Used for bulk actions to prepare test data. Is useful when you need to prepare a lot of data.
This step consists of 3 parts:

1. write sql ddl schema file (optional) - describe all tables/schemas/privileges needed to be created
2. prepare data in a csv file (optional)
3. call Catcher's prepare step to populate csv content into the database

Both sql schema and csv file supports templates.

Create **resources/schema.sql**::

    CREATE TABLE foo(
                    user_id      integer    primary key,
                    email        varchar(36)    NOT NULL
                );

Create **resources/foo.csv** which generates rows for all users in **users** variable::

    user_id,email
    {%- for user in users %}
    {{ user.uuid }},{{ user.email }}
    {%- endfor -%}

Call prepare step and tell it to create **foo** table and use **foo.csv** to populate it::

    prepare:
      populate:
        mysql:
          conf: '{{ mysql_conf }}'
          schema: schema.sql
          data:
            foo: foo.csv

**Important**:

* populate step is designed to be supported by all steps (in future). Currently it is supported only by Postges/Oracle/MSSql/MySql/SQLite steps.
* to populate json as Postgres Json data type you need to use **use_json: true** flag

Schema **resources/pg_schema.sql**::

    CREATE TABLE my_table(
                    user_id      integer    primary key,
                    payload      json       NOT NULL
                );

Data file **resources/json_table.csv**::

    user_id,payload\n
    1,{\"date\": \"1990-07-20\"}

Postgres prepare step::

    prepare:
        populate:
            postgres:
                conf: '{{ postgres }}'
                schema: pg_schema.sql
                data:
                    my_table: json_table.csv
                use_json: true

**Hint**: You can specify multiple tables and databases::

    prepare:
        populate:
            postgres:
                conf: '{{ postgres }}'
                schema: pg_schema.sql
                data:
                    table1: resource1.csv
                    table2: resource2.csv
            mysql:
                conf: '{{ mysql_conf }}'
                schema: schema.sql
                data:
                    foo: foo.csv

You can find more information in a separate document `prepare <https://catcher-modules.readthedocs.io/en/latest/source/prepare_expect.html>`_

For the module documentation see catcher-modules `prepare step <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.service.html#catcher-modules-service-prepare-module>`_.

expect - allows you to bulk-check data
--------------------------------------
This is the opposite for prepare. It compares expected data from csv to what you have in the database.
csv file supports templates.

**Important**:

* populate step is designed to be supported by all steps (in future). Currently it is supported only by Postges/Oracle/MSSql/MySql/SQLite steps.
* Schema comparison is not implemented.
* You can use strict comparison (only data from csv should be in the table, in the same order as csv) or the default one (just check if the data is there)

Create **resources/foo.csv** expected file::

    user_id,email
    {%- for user in users %}
    {{ user.uuid }},{{ user.email }}
    {%- endfor -%}

Run expect step for both tables::

    expect:
        compare:
            postgres:
                conf: 'test:test@localhost:5433/test'
                data:
                    foo: foo.csv

**Hint**: You can specify multiple tables and databases::

    expect:
        compare:
            postgres:
                conf: '{{ postgres }}'
                data:
                    foo: foo.csv
                    bar: bar.csv
            mysql:
                conf: '{{ mysql_conf }}'
                data:
                    foo: foo.csv
                    bar: bar.csv

You can find more information in a separate document `expect <https://catcher-modules.readthedocs.io/en/latest/source/prepare_expect.html#expect>`_

For the module documentation see catcher-modules `expect step <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.service.html#catcher-modules-service-expect-module>`_.

email - send/receive emails
---------------------------
Allows you to send and receive emails via `IMAP <https://en.wikipedia.org/wiki/Internet_Message_Access_Protocol>`_ protocol.

Find unread message containing blog name in **subject**, mark as read and register in **mail** variable::

    email:
      receive:
          config:
            host: 'imap.google.com'
            user: 'my_user@google.com'
            pass: 'my_pass'
          filter: {unread: true, subject: 'justtech.blog'}
          ack: true
          limit: 1
      register: {mail: '{{ OUTPUT }}'}

Send message::

    email:
      send:
          config: '{{ email_conf }}'
          to: 'test@test.com'
          from: 'me@test.com'
          subject: 'test_subject'
          html: '
          <html>
              <body>
                <p>Hi,<br>
                   How are you?<br>
                   <a href="http://example.com">Link</a>
                </p>
              </body>
          </html>'

For the module documentation see catcher-modules `email <https://catcher-modules.readthedocs.io/en/latest/source/catcher_modules.service.html#catcher-modules-service-email-module>`_.

airflow - interact with Apache Airflow
--------------------------------------
Allows you to run dag sync/async, get xcom and populate connections in Apache `Airflow <https://airflow.apache.org/>`_
workflow management platform.

Run dag and wait for it to be completed or fail after 50 seconds or if dag fails::

    - airflow:
        run:
            config:
                db_conf: 'airflow:airflow@localhost:5433/airflow'
                url: 'http://127.0.0.1:8080'
            dag_id: 'init_data_sync'
            sync: true
            wait_timeout: 50

**Hint**: if you'd like to populate Airflow connections based on Catcher's inventory file use **populate_connections** flag.

For more information see separate document `airflow <https://catcher-modules.readthedocs.io/en/latest/source/airflow.html>`_.
You may also find `catcher-airflow-example <https://github.com/comtihon/catcher_airflow_example>`_ github repo useful.
