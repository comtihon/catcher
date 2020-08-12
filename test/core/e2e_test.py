import os
import subprocess
from os.path import join

from test import TEST_DIR
from test.abs_test_class import TestClass
from catcher.utils import file_utils
from catcher import __main__


class E2ETest(TestClass):
    def __init__(self, method_name):
        super().__init__('e2e_test', method_name)

    def setUp(self):
        super().setUp()
        file_utils.ensure_empty(join(os.getcwd(), TEST_DIR, 'steps'))

    def tearDown(self):
        super().tearDown()
        file_utils.remove_dir(join(os.getcwd(), TEST_DIR, 'steps'))
        file_utils.remove_dir(join(os.getcwd(), TEST_DIR, 'reports'))

    def test_can_run(self):
        self.populate_file('main.yaml', '''---
                steps:
                    - check: 
                        equals: {the: 'life', is: 'life'}  # na-na, na-na-na
                ''')
        self._run_test(self.test_dir)

    def test_check_output(self):
        self.populate_file('one.yaml', '''---
                        steps:
                            - echo: {from: '{{ "test" | hash }}'}
                            - check: 
                                equals: {the: 'life', is: 'life'}
                        ''')
        self.populate_file('two.yaml', '''---
                        steps:
                            - echo: {from: '{{ "test" | hash }}'}
                            - check: 
                                equals: {the: 'life', is_not: 'life'}
                            - echo: 'hello world'
                        ''')
        self.populate_file('three.yaml', '''---
                        steps:
                            - echo: {from: '{{ "test" | hash }}'}
                            - check: 
                                equals: {the: 'life', is: 'life'}
                        ''')
        output = self._run_test(self.test_dir + ' --no-color', expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 3. Success: 2, Fail: 1. Total: 67%', lines[-4])
        self.assertEqual('Test one: pass', to_compare[-3])
        self.assertEqual('Test three: pass', to_compare[-2])
        self.assertEqual('Test two: fail, on step 2', to_compare[-1])

    def test_check_output_skipp_test(self):
        self.populate_file('one.yaml', '''---
                                ignore: true
                                steps:
                                    - echo: {from: '{{ "test" | hash }}'}
                                    - check: 
                                        equals: {the: 'life', is: 'life'}
                                ''')
        self.populate_file('two.yaml', '''---
                                steps:
                                    - echo: {from: '{{ "test" | hash }}'}
                                    - check: 
                                        equals: {the: 'life', is: 'life'}
                                    - echo: 'hello world'
                                ''')
        output = self._run_test(self.test_dir + ' --no-color')
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 0, Skipped: 1. Total: 100%', lines[-3])
        self.assertEqual('Test one: skipped', to_compare[-2])
        self.assertEqual('Test two: pass', to_compare[-1])

    def test_check_output_run_on_include(self):
        self.populate_step('steps/include.yaml', '''---
                                steps:
                                    - echo: {from: 'I am include'}
                                    - check: 
                                        equals: {the: 'life', is: 'life'}
                                ''')
        self.populate_file('two.yaml', '''---
                                include: steps/include.yaml
                                steps:
                                    - echo: {from: '{{ "test" | hash }}'}
                                    - check: 
                                        equals: {the: 'life', is_not: 'life'}
                                    - echo: 'hello world'
                                ''')
        self.populate_file('three.yaml', '''---
                                steps:
                                    - echo: {from: '{{ "test" | hash }}'}
                                    - check: 
                                        equals: {the: 'life', is: 'life'}
                                ''')
        output = self._run_test(self.test_dir + ' --no-color', expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%', to_compare[-3])
        self.assertEqual('Test three: pass', to_compare[-2])
        self.assertEqual('Test two: fail, on step 2', to_compare[-1])

    def test_check_output_ignored_include(self):
        self.populate_step('steps/include.yaml', '''---
                                        ignore: true
                                        steps:
                                            - echo: {from: 'I am include'}
                                            - check: 
                                                equals: {the: 'life', is: 'life'}
                                        ''')
        self.populate_file('two.yaml', '''---
                                        include: steps/include.yaml
                                        steps:
                                            - echo: {from: '{{ "test" | hash }}'}
                                            - check: 
                                                equals: {the: 'life', is_not: 'life'}
                                            - echo: 'hello world'
                                        ''')
        self.populate_file('three.yaml', '''---
                                        steps:
                                            - echo: {from: '{{ "test" | hash }}'}
                                            - check: 
                                                equals: {the: 'life', is: 'life'}
                                        ''')
        output = self._run_test(self.test_dir + ' --no-color', expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%', to_compare[-3])
        self.assertEqual('Test three: pass', to_compare[-2])
        self.assertEqual('Test two: fail, on step 2', to_compare[-1])

    def test_failed_include_ignore_test(self):
        self.populate_file('two.yaml', '''---
                                        include: non_existent.yaml
                                        ignore: true
                                        steps:
                                            - echo: 'hello world'
                                        ''')
        output = self._run_test(self.test_dir + ' --no-color')
        print(output)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 1. Success: 0, Fail: 0, Skipped: 1. Total: 100%', to_compare[0])
        self.assertEqual('INFO:catcher:Test two skipped.', to_compare[1])

    def test_check_output_run_on_action(self):
        self.populate_step('steps/include.yaml', '''---
                                        steps:
                                            - echo: {from: 'I am include'}
                                            - check: 
                                                equals: {the: 'life', is: 'life'}
                                        ''')
        self.populate_file('two.yaml', '''---
                                        include: 
                                            - file: steps/include.yaml
                                              as: run_me
                                        steps:
                                            - run:
                                                include: run_me
                                            - check: 
                                                equals: {the: 'life', is_not: 'life'}
                                            - echo: 'hello world'
                                        ''')
        self.populate_file('three.yaml', '''---
                                        steps:
                                            - echo: {from: '{{ "test" | hash }}'}
                                            - check: 
                                                equals: {the: 'life', is: 'life'}
                                        ''')
        output = self._run_test(self.test_dir + ' --no-color', expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%', to_compare[-3])
        self.assertEqual('Test three: pass', to_compare[-2])
        self.assertEqual('Test two: fail, on step 2', to_compare[-1])

    def test_check_output_ignored_run_on_action(self):
        self.populate_step('steps/include.yaml', '''---
                                        ignore: true
                                        steps:
                                            - echo: {from: 'I am include'}
                                            - check: 
                                                equals: {the: 'life', is: 'life'}
                                        ''')
        self.populate_file('two.yaml', '''---
                                        include: 
                                            - file: steps/include.yaml
                                              as: run_me
                                        steps:
                                            - run:
                                                include: run_me
                                            - check: 
                                                equals: {the: 'life', is_not: 'life'}
                                            - echo: 'hello world'
                                        ''')
        self.populate_file('three.yaml', '''---
                                        steps:
                                            - echo: {from: '{{ "test" | hash }}'}
                                            - check: 
                                                equals: {the: 'life', is: 'life'}
                                        ''')
        output = self._run_test(self.test_dir + ' --no-color', expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%',
                         to_compare[-3])
        self.assertEqual('Test three: pass', to_compare[-2])
        self.assertEqual('Test two: fail, on step 2', to_compare[-1])

    def test_run_summary_with_output(self):
        self.populate_file('main.yaml', '''---
                        steps:
                            - check: 
                                equals: {the: 'life', is: 'life'}  # na-na, na-na-na
                        ''')
        output = self._run_test(self.test_dir + ' --no-color -p json')
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-2:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 1. Success: 1, Fail: 0. Total: 100%', to_compare[-2])
        self.assertEqual('Test main: pass', to_compare[-1])

    def test_run_output_include_only(self):
        self.populate_file('main.yaml', '''---
                include: 
                    - steps/simple_file.yaml
                ''')
        self.populate_step('steps/simple_file.yaml', '''---
                include: 
                    - steps/other_simple_file.yaml
                variables:
                    foo: bar
                steps:
                    - echo: {from: '{{ foo }}'}
                ''')
        self.populate_step('steps/other_simple_file.yaml', '''---
                include: 
                    - steps/simple_file.yaml
                variables:
                    foo: baz
                steps:
                    - echo: {from: '{{ foo }}'}
                ''')
        output = self._run_test(self.test_dir + ' --no-color', expected_code=1)
        lines = output.strip().split('\n')
        self.assertTrue('Circular dependencies' in lines[-3])
        self.assertEqual('INFO:catcher:Test run 1. Success: 0, Fail: 1. Total: 0%', lines[-2])
        self.assertEqual('Test main: fail, on step 0', lines[-1])

    def test_run_output_limited(self):
        pass

    def test_run_output_final(self):
        pass

    def _run_test(self, args: str, expected_code=0):
        process = subprocess.Popen('python {} {}'.format(__main__.__file__, args).split(' '),
                                   cwd=join(os.getcwd(), TEST_DIR),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()
        if expected_code != process.returncode:
            print(stderr)
            self.fail('Got return code {}, expected {}'.format(process.returncode, expected_code))
        return stderr

    @staticmethod
    def populate_step(file: str, content: str):
        with open(join(os.getcwd(), TEST_DIR, file), 'w') as f:
            f.write(content)
