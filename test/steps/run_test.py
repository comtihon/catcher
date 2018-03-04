from os.path import join

import os

from catcher.core.runner import Runner
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
    def test_run_ignore_errors(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ test - 2 }}', to: main1.output, ignore_errors: true}
            - echo: {from: 'test2', to: main2.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(not os.path.exists(join(self.test_dir, 'main1.output')))
        self.assertTrue(check_file(join(self.test_dir, 'main2.output'), 'test2'))
