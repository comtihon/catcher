import os
from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class VariablesTest(TestClass):
    def __init__(self, method_name):
        super().__init__('variables_test', method_name)

    # newly registered variables override everything
    def test_register_override_cmd(self):
        self.populate_file('main.yaml', '''---
        variables:
            foo: baz
        steps:
            - echo: 
                actions: 
                    - {from: 'bar', register: {foo: '{{ OUTPUT }}'}}
                    - {from: '{{ foo }}', to: one.output}
            
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, cmd_env={'foo': 'bad'})
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bar'))

    # variables, passed via cmd `e` options should override all variables
    def test_cmd_override_all(self):
        self.populate_file('inventory.yml', '''---
                foo2: baz
                ''')
        self.populate_file('main.yaml', '''---
        variables:
            foo: baz
        steps:
            - echo: 
                actions: 
                    - {from: '{{ foo }}', to: one.output}
                    - {from: '{{ foo2 }}', to: two.output}

        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        join(self.test_dir, 'inventory.yml'),
                        cmd_env={'foo': 'bad', 'foo2': 'bad'})
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bad'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'bad'))

    # test computed variables available later
    def test_computed_available_later(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: 
                actions: 
                    - {from: 'hello', register: {foo: 'bar'}}
                    - {from: '{{ foo }}', to: one.output}
            
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bar'))

    # test computed available in the other step
    def test_computed_available_other_step(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'hello', register: {foo: 'bar'}}
            - echo: {from: '{{ foo }}', to: one.output}
            
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bar'))

    # test var can be computed from the template
    def test_computed_with_template(self):
        self.populate_file('main.yaml', '''---
        variables:
            path: /home/user
            test: main.yml
        steps:
            - echo: {from: 'hello', register: {foo: '{{ path }}/{{ test }}'}}
            - echo: {from: '{{ foo }}', to: one.output}
            
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '/home/user/main.yml'))

    # test if env vars included from inventory
    def test_env_vars_included(self):
        os.environ['FOO'] = '1'
        self.populate_file('main.yaml', '''---
        steps:
            - check: {equals: {the: '{{ FOO }}', is: '1'}}

        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        self.assertTrue(runner.run_tests())

    # env var should be overridden with any other var
    def test_var_override_env(self):
        os.environ['FOO'] = '1'
        self.populate_file('main.yaml', '''---
        variables:
            FOO: 2
        steps:
            - check: {equals: {the: '{{ FOO }}', is: '2'}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_env_var_in_vars(self):
        os.environ['FOO'] = '1'
        self.populate_file('main.yaml', '''---
                variables:
                    foo: '{{ FOO }}'
                steps:
                    - check: {equals: {the: '{{ foo }}', is: '1'}}

                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, system_environment=dict(os.environ))
        self.assertTrue(runner.run_tests())

    def test_var_in_run_as_obj(self):
        self.populate_resource('test.csv', "email,id\n"
                                           "{%- for user in users %}\n"
                                           "{{ user.email }},{{ user.id }}\n"
                                           "{%- endfor -%}"
                               )
        self.populate_file('main.yaml', '''---
                                variables:
                                    users:
                                        - email: 'first@test.de'
                                          id: 1
                                        - email: 'second@test.de'
                                          id: 2
                                include: 
                                    file: one.yaml
                                    as: one
                                steps:
                                    - run: 
                                        include: 'one'
                                        variables:
                                            users: '{{ users[:1] }}'
                                ''')
        self.populate_file('one.yaml', '''---
                                steps:
                                    - echo: {from_file: 'test.csv', to: res.output}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'res.output'), 'email,id\nfirst@test.de,1'))
