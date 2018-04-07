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
        self.assertTrue(not os.path.exists(join(self.test_dir, 'main1.output')))
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
