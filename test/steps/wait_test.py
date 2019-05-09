from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class WaitTest(TestClass):
    def __init__(self, method_name):
        super().__init__('wait', method_name)

    def test_wait_fixed(self):
        self.populate_file('main.yaml', '''---
            steps:
                - echo: {from: '{{ NOW_TS }}', register: {before: '{{ OUTPUT }}'}}
                - wait: {seconds: 1}
                - echo: {from: '{{ NOW_TS }}', register: {after: '{{ OUTPUT }}'}}
                - check: {equals: {the: '{{ after - before >= 1 }}', is: true}}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_wait_service(self):
        """
        variables should be accessible both reads and writes for commands in for-block
        """
        self.populate_file('main.yaml', '''---
                    variables:
                        counter: 0
                    steps:
                        - wait: 
                            seconds: 1
                            for:
                                echo: {from: '{{ counter + 1}}', register: {counter: '{{ OUTPUT }}'}}
                        - check: {equals: {the: '{{ counter }}', is: 1}}
                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_wait_success(self):
        """
        wait should return as soon as `for` succeeds
        """
        self.populate_file('main.yaml', '''---
                            variables:
                                counter: 0
                            steps:
                                - wait: 
                                    seconds: 1
                                    for:
                                        - echo: {from: '{{ counter + 1}}', register: {counter: '{{ OUTPUT }}'}}
                                        - check: {equals: {the: '{{ counter }}', is: 1}}
                                - check: {equals: {the: '{{ counter }}', is: 1}}
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_wait_failure(self):
        """
        wait should stop after delay if `for` fails
        """
        self.populate_file('main.yaml', '''---
                                    variables:
                                        counter: 0
                                    steps:
                                        - echo: {from: '{{ NOW_TS }}', register: {before: '{{ OUTPUT }}'}}
                                        - wait: 
                                            seconds: 1
                                            for:
                                                check: {equals: {the: '{{ counter }}', is: 1}}
                                        - echo: {from: '{{ NOW_TS }}', register: {after: '{{ OUTPUT }}'}}
                                        - check: {equals: {the: '{{ after - before >= 1 }}', is: true}}
                                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
