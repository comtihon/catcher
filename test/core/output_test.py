import os
from os.path import join

import requests_mock

from catcher.core.runner import Runner
from catcher.utils.file_utils import read_file
from test.abs_test_class import TestClass
from test.test_utils import check_file


class OutputTest(TestClass):
    def __init__(self, method_name):
        super().__init__('output_test', method_name)

    def test_run_multiple_steps(self):
        self.populate_file('main.yaml', '''---
        variables:
            foo: [bar, baz]
        steps:
            - echo: {from: '{{ foo }}'}
            - check: 
                any:
                    of: '{{ foo }}'
                    equals: 'baz'
            - check: 
                any:
                    of: [bar, baz]
                    equals: 'baz'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())

    def test_step_failed(self):
        pass

    def test_run_multiple_tests(self):
        pass

    def test_run_with_include(self):
        pass

    def test_run_with_include_named(self):
        pass
