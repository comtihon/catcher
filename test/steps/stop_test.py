from os.path import join

import psycopg2

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class StopTest(TestClass):
    def __init__(self, method_name):
        super().__init__('stop', method_name)

    @property
    def conf(self):
        return "dbname=test user=test host=localhost password=test port=5433"

    def setUp(self):
        super().setUp()
        conn = psycopg2.connect(self.conf)
        cur = conn.cursor()
        cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer);")
        cur.execute("CREATE TABLE migration (id serial PRIMARY KEY, hash varchar(255));")
        conn.commit()
        cur.close()
        conn.close()

    def tearDown(self):
        super().tearDown()
        conn = psycopg2.connect(self.conf)
        cur = conn.cursor()
        cur.execute("DROP TABLE test;")
        cur.execute("DROP TABLE migration;")
        conn.commit()
        cur.close()
        conn.close()

    def test_write_once(self):
        self.populate_file('test_inventory.yml', '''
        postgres:
            dbname: test
            user: test
            password: test
            host: localhost
            port: 5433
        ''')
        self.populate_file('main.yaml', '''---
            variables:
                hash: 'migration_1'
            steps:
                - postgres:
                    request:
                        conf: '{{ postgres }}'
                        query: "select count(*) from migration where hash = '{{ hash }}';"
                    register: {result: '{{ OUTPUT }}'}
                - stop: 
                    if: 
                        equals: {the: '{{ result }}', is: 1}
                - postgres:
                    actions:
                        - request:
                            conf: '{{ postgres }}'
                            query: 'insert into test(id, num) values(3, 3);'
                        - request:
                            conf: '{{ postgres }}'
                            query: "insert into migration(id, hash) values(1, '{{ hash }}');"
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'test_inventory.yml'))
        self.assertTrue(runner.run_tests())
        self.assertTrue(runner.run_tests())
        conn = psycopg2.connect(self.conf)
        cur = conn.cursor()
        cur.execute("select count(*) from test")
        response = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        self.assertEqual([(1,)], response)

    def test_stop_from_include(self):
        self.populate_file('test_inventory.yml', '''
        postgres:
            dbname: test
            user: test
            password: test
            host: localhost
            port: 5433
        ''')
        self.populate_file('main.yaml', '''---
        include: 
            file: migration.yaml
            as: migrate
        steps:
            - run: migrate.check
            - postgres:
                request:
                    conf: '{{ postgres }}'
                    query: "insert into test(id, num) values(3, 3);"
            - run: migrate.commit
        ''')
        self.populate_file('migration.yaml', '''---
        steps:
            - postgres:
                request:
                    conf: '{{ postgres }}'
                    query: "select count(*) from migration where hash = '{{ TEST_NAME }}';"
                register: {result: '{{ OUTPUT }}'}
                tag: check
                name: 'check_migration_{{ TEST_NAME }}'
            - stop: 
                if: 
                    equals: {the: '{{ result }}', is: 1}
                tag: check
                name: 'stop_if_already_run_{{ TEST_NAME }}'
            - postgres:
                request:
                    conf: '{{ postgres }}'
                    query: "insert into migration(id, hash) values(1, '{{ TEST_NAME }}');"
                tag: commit
                name: 'commit_migration_{{ TEST_NAME }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'test_inventory.yml'))
        self.assertTrue(runner.run_tests())
        self.assertTrue(runner.run_tests())
        conn = psycopg2.connect(self.conf)
        cur = conn.cursor()
        cur.execute("select count(*) from test")
        response = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        self.assertEqual([(1,)], response)
