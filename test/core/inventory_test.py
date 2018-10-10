import ast
import os
from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file, read_file


class InventoryTest(TestClass):
    def __init__(self, method_name):
        super().__init__('inventory_test', method_name)

    # test inventory vars available in test
    def test_inventory_vars_available(self):
        self.populate_file('inventory.yml', '''---
        prod_url: http://prod.url
        foo: bar
        ''')
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ prod_url }}', to: main1.output}
            - echo: {from: '{{ foo }}', to: main2.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'inventory.yml'))
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'main1.output'), 'http://prod.url'))
        self.assertTrue(check_file(join(self.test_dir, 'main2.output'), 'bar'))

    # test inventory vars available in include
    def test_inventory_vars_available_in_include(self):
        self.populate_file('inventory.yml', '''---
        foo: bar
        ''')
        self.populate_file('main.yaml', '''---
        include: one.yaml
        steps:
            - echo: {from: '{{ foo }}', to: main.output}
        ''')
        self.populate_file('one.yaml', '''---
        steps:
            - echo: {from: '{{ foo }}', to: include.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'inventory.yml'))
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'include.output'), 'bar'))

    # test inventory vars can be overridden with test vars
    def test_override_inventory(self):
        self.populate_file('inventory.yml', '''---
        foo: bar
        ''')
        self.populate_file('main.yaml', '''---
        variables:
            foo: baz
        steps:
            - echo: {from: '{{ foo }}', to: main.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'inventory.yml'))
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'main.output'), 'baz'))

    def test_cmd_variable_override_inventory(self):
        self.populate_file('inventory.yml', '''---
        one: bar
        ''')
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ one }}', to: 1.output}
            - echo: {from: '{{ two }}', to: 2.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'inventory.yml'),
                        environment={'one': 'baz', 'two': 'bax'})
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, '1.output'), 'baz'))
        self.assertTrue(check_file(join(self.test_dir, '2.output'), 'bax'))

    # env var can be set in vars
    def test_env_var_in_inventory(self):
        os.environ['FOO'] = '1'
        self.populate_file('inventory.yml', '''---
        foo: '{{ FOO }}'
        ''')
        self.populate_file('main.yaml', '''---
        steps:
            - check: {equals: {the: '{{ foo }}', is: '1'}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'inventory.yml'))
        self.assertTrue(runner.run_tests())

    # env var can be set inside other vars
    def test_env_vars_complex(self):
        os.environ['USER'] = 'user'
        os.environ['PASSWORD'] = '********'
        self.populate_file('inventory.yml', '''---
        database_conf:
            username: '{{ USER }}'
            password: '{{ PASSWORD }}'
        ''')
        self.populate_file('main.yaml', '''---
        steps:
           - echo: {from: '{{ database_conf }}', to: database_conf.output}
           - check: {equals: {the: '{{ database_conf.username }}', is: 'user'}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'inventory.yml'))
        self.assertTrue(runner.run_tests())
        content = ast.literal_eval(read_file(join(self.test_dir, 'database_conf.output')))
        self.assertEquals(content, {'username': 'user', 'password': '********'})
