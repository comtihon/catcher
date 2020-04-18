import os
import re
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
        output = self._run_test(self.test_dir, expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 3. Success: 2, Fail: 1. Total: 67%',
                         self.clean_output(lines[-4]))
        self.assertEqual('Test one.yaml: pass', self.clean_output(to_compare[-3]))
        self.assertEqual('Test three.yaml: pass', self.clean_output(to_compare[-2]))
        self.assertEqual('Test two.yaml: fail, on step 2', self.clean_output(to_compare[-1]))

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
        output = self._run_test(self.test_dir)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 0, Skipped: 1. Total: 100%',
                         self.clean_output(lines[-3]))
        self.assertEqual('Test one.yaml: skipped', self.clean_output(to_compare[-2]))
        self.assertEqual('Test two.yaml: pass', self.clean_output(to_compare[-1]))

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
        output = self._run_test(self.test_dir, expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%',
                         self.clean_output(to_compare[-3]))
        self.assertEqual('Test three.yaml: pass', self.clean_output(to_compare[-2]))
        self.assertEqual('Test two.yaml: fail, on step 2', self.clean_output(to_compare[-1]))

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
        output = self._run_test(self.test_dir, expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%',
                         self.clean_output(to_compare[-3]))
        self.assertEqual('Test three.yaml: pass', self.clean_output(to_compare[-2]))
        self.assertEqual('Test two.yaml: fail, on step 2', self.clean_output(to_compare[-1]))

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
        output = self._run_test(self.test_dir, expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%',
                         self.clean_output(to_compare[-3]))
        self.assertEqual('Test three.yaml: pass', self.clean_output(to_compare[-2]))
        self.assertEqual('Test two.yaml: fail, on step 2', self.clean_output(to_compare[-1]))

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
        output = self._run_test(self.test_dir, expected_code=1)
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-3:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 2. Success: 1, Fail: 1. Total: 50%',
                         self.clean_output(to_compare[-3]))
        self.assertEqual('Test three.yaml: pass', self.clean_output(to_compare[-2]))
        self.assertEqual('Test two.yaml: fail, on step 2', self.clean_output(to_compare[-1]))

    def test_run_summary_with_output(self):
        self.populate_file('main.yaml', '''---
                        steps:
                            - check: 
                                equals: {the: 'life', is: 'life'}  # na-na, na-na-na
                        ''')
        output = self._run_test(self.test_dir + ' -p json')
        lines = output.strip().split('\n')
        to_compare = sorted(lines[-2:])  # need to sort it, as output order is not guaranteed in CI
        self.assertEqual('INFO:catcher:Test run 1. Success: 1, Fail: 0. Total: 100%',
                         self.clean_output(to_compare[-2]))
        self.assertEqual('Test main.yaml: pass', self.clean_output(to_compare[-1]))

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
        output = self._run_test(self.test_dir, expected_code=1)
        lines = output.strip().split('\n')
        self.assertEqual('INFO:catcher:Test run 0. Success: 0, Fail: 0. Total: 0%',
                         self.clean_output(lines[-1]))

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

    @staticmethod
    def clean_output(string):
        ansi_regex = r'\x1b(' \
                     r'(\[\??\d+[hl])|' \
                     r'([=<>a-kzNM78])|' \
                     r'([\(\)][a-b0-2])|' \
                     r'(\[\d{0,2}[ma-dgkjqi])|' \
                     r'(\[\d+;\d+[hfy]?)|' \
                     r'(\[;?[hf])|' \
                     r'(#[3-68])|' \
                     r'([01356]n)|' \
                     r'(O[mlnp-z]?)|' \
                     r'(/Z)|' \
                     r'(\d+)|' \
                     r'(\[\?\d;\d0c)|' \
                     r'(\d;\dR))'
        ansi_escape = re.compile(ansi_regex, flags=re.IGNORECASE)
        return ansi_escape.sub('', string)
