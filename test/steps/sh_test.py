from os.path import join

import pytest
from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import read_file, check_file


class ShTest(TestClass):
    def __init__(self, method_name):
        super().__init__('sh_test', method_name)

    def test_list_directory(self):
        self.populate_file('main.yaml', '''---
        steps:
            - sh:
                command: 'ls -la'
                path: '{{ CURRENT_DIR }}'
                register: {content: '{{ OUTPUT }}'}
            - echo: {from: '{{ content }}', to: 'debug.output'}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        file = read_file(join(self.test_dir, 'debug.output'))
        self.assertTrue('resources' in file)

    # try to delete non existent directory and fail test with non zero return code.
    def test_run_negative(self):
        self.populate_file('main.yaml', '''---
                steps:
                    - sh:
                        command: 'rm foobarbaz'
                    - echo: {from: '{{ content }}', to: 'debug.output'}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertFalse(runner.run_tests())

    @pytest.mark.skip(reason="Disabled for CI, as it may run tests in docker")
    def test_run_in_docker(self):
        self.populate_file('main.yaml', '''---
                        variables:
                            docker: true
                        steps:
                            - sh:
                                command: "grep 'docker|lxc' /proc/1/cgroup"
                                return_code: 1
                                ignore_errors: true
                                register: {docker: false}
                            - echo: {from: '{{ docker }}', to: 'debug.output'}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'debug.output'), 'False'))
