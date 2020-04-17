import os
import subprocess
from os.path import join

from test import TEST_DIR
from test.abs_test_class import TestClass
from catcher.utils import logger, file_utils


class E2ETest(TestClass):
    def __init__(self, method_name):
        super().__init__('e2e_test', method_name)

    def setUp(self):
        super().setUp()
        file_utils.ensure_empty(join(os.getcwd(), TEST_DIR, 'steps'))

    def tearDown(self):
        super().tearDown()
        file_utils.remove_dir(join(os.getcwd(), TEST_DIR, 'steps'))

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
        self.assertEqual(
            'INFO:catcher:Test run {}. Success: {}, Fail: {}. Total: {}'.format(logger.blue('3'),
                                                                                logger.green('2'),
                                                                                logger.red('1'),
                                                                                logger.light_green('67%')),
            lines[-4])
        self.assertEqual('Test one.yaml: ' + logger.green('pass'), lines[-3])
        self.assertEqual('Test two.yaml: ' + logger.red('fail') + ', on step 2', lines[-2])
        self.assertEqual('Test three.yaml: ' + logger.green('pass'), lines[-1])

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
        self.assertEqual(
            'INFO:catcher:Test run {}. Success: {}, Fail: {}. Total: {}'.format(logger.blue('2'),
                                                                                logger.green('1'),
                                                                                logger.red('1'),
                                                                                logger.yellow('50%')),
            lines[-3])
        self.assertEqual('Test two.yaml: ' + logger.red('fail') + ', on step 2', lines[-2])
        self.assertEqual('Test three.yaml: ' + logger.green('pass'), lines[-1])

    def test_check_outut_run_on_action(self):
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
        self.assertEqual(
            'INFO:catcher:Test run {}. Success: {}, Fail: {}. Total: {}'.format(logger.blue('2'),
                                                                                logger.green('1'),
                                                                                logger.red('1'),
                                                                                logger.yellow('50%')),
            lines[-3])
        self.assertEqual('Test two.yaml: ' + logger.red('fail') + ', on step 2', lines[-2])
        self.assertEqual('Test three.yaml: ' + logger.green('pass'), lines[-1])

    def _run_test(self, args: str, expected_code=0):
        process = subprocess.Popen('python ../../../../catcher/__main__.py {}'.format(args).split(' '),
                                   cwd=join(os.getcwd(), TEST_DIR),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()
        self.assertEqual(expected_code, process.returncode)
        return stderr

    @staticmethod
    def populate_step(file: str, content: str):
        with open(join(os.getcwd(), TEST_DIR, file), 'w') as f:
            f.write(content)
