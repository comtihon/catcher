import os
from os.path import join

import requests_mock

from catcher.core.runner import Runner
from catcher.utils.file_utils import read_file
from test.abs_test_class import TestClass
from test.test_utils import check_file


class RunTest(TestClass):
    def __init__(self, method_name):
        super().__init__('run_test', method_name)

    # test run one action
    def test_run_one_action(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'test', to: main.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'main.output'), 'test'))

    # run action and register variable in it
    def test_run_register(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'user-{{ RANDOM_STR }}', register: {uuid: '{{ OUTPUT }}'}}
            - echo: {from: '{{ uuid }}', to: main.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        file = read_file(join(self.test_dir, 'main.output'))
        self.assertTrue(file.startswith('user'))
        self.assertTrue('{{' not in file)  # template was filled in

    # test run several actions
    def test_run_several_actions(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'test1', to: main1.output}
            - echo: {from: 'test2', to: main2.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'main1.output'), 'test1'))
        self.assertTrue(check_file(join(self.test_dir, 'main2.output'), 'test2'))

    # test run ignore errors
    @requests_mock.mock()
    def test_run_ignore_errors(self, m):
        m.get('http://test.com', status_code=500)
        self.populate_file('main.yaml', '''---
        steps:
            - http: {get: {url: 'http://test.com', response_code: 200}, ignore_errors: true}
            - echo: {from: 'test2', to: main2.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'main2.output'), 'test2'))

    def test_run_named(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: 
                from: 'user-{{ RANDOM_STR }}'
                register: {uuid: '{{ OUTPUT }}'}
                name: 'first'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_run_named_variables(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'user-{{ RANDOM_STR }}', register: {uuid: '{{ OUTPUT }}'}}
            - echo: 
                from: '{{ uuid }}'
                to: main.output
                name: 'Save user {{ uuid }} to main.output'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_run_system_variables(self):
        os.environ["SECRET_PASSWORD"] = "123"
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ SECRET_PASSWORD }}', to: sys_env.output}
        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'sys_env.output'), '123'))

    def test_run_skip_if_short(self):
        self.populate_file('main.yaml', '''---
                variables:
                    no_output: true
                steps:
                    - echo:
                        from: 'hello world'
                        to: main1.output
                        skip_if: '{{ no_output }}'
                    - echo: {from: 'test2', to: main2.output}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(not os.path.exists(join(self.test_dir, 'main1.output')))
        self.assertTrue(check_file(join(self.test_dir, 'main2.output'), 'test2'))

    def test_run_skip_if_long(self):
        self.populate_file('main.yaml', '''---
                        variables:
                            user_name: 'test'
                        steps:
                            - echo:
                                from: 'hello world'
                                to: main1.output
                                skip_if:
                                    equals: {the: '{{ user_name }}', is: 'test'}
                            - echo: {from: 'test2', to: main2.output}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(not os.path.exists(join(self.test_dir, 'main1.output')))

    def test_run_skip_if_multiple(self):
        self.populate_file('main.yaml', '''---
                                variables:
                                    list: ['a', 'b', 'c']
                                steps:
                                    - echo:
                                        from: 'hello world'
                                        to: main1.output
                                        skip_if:
                                            or:
                                                - contains: {the: '1', in: '{{ list }}'}
                                                - equals: {the: '{{ list[0] }}', is: 'a'}
                                                - contains: {the: 'b', in: '{{ list }}'}
                                    - echo: {from: 'test2', to: main2.output}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(not os.path.exists(join(self.test_dir, 'main1.output')))

    def test_run_ignore_test(self):
        self.populate_file('main.yaml', '''---
                ignore: true # for some reason this test is not working
                steps:
                    - check: {equals: {the: true, is: false}}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_ignore_condition(self):
        os.environ['CLOUD'] = 'AWS'
        self.populate_file('main.yaml', '''---
                        ignore: 
                            equals: {the: '{{ CLOUD }}', is: 'AWS'}
                        steps:
                            - check: {equals: {the: true, is: false}}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, system_environment=dict(os.environ))
        self.assertTrue(runner.run_tests())

        os.environ['CLOUD'] = 'Marathon'
        self.populate_file('main.yaml', '''---
                                ignore: 
                                    equals: {the: '{{ CLOUD }}', is: 'AWS'}
                                steps:
                                    - check: {equals: {the: true, is: false}}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, system_environment=dict(os.environ))
        self.assertFalse(runner.run_tests())

