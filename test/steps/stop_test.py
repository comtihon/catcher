from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class StopTest(TestClass):
    def __init__(self, method_name):
        super().__init__('stop', method_name)

    def test_stop(self):
        self.populate_file('main.yaml', '''---
            variables:
                counter: 0
            steps:
                - echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
                - stop: 
                    if: 
                        equals: '{{ counter > 1 }}'
                - echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
                - stop: 
                    if: 
                        equals: '{{ counter > 1 }}'
                - echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
                - check: {equals: {the: '{{ counter }}', is: 2}}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_stop_from_include(self):
        self.populate_file('main.yaml', '''---
        include: 
            file: migration.yaml
            as: migrate
        variables:
            counter: 0
        steps:
            - run: migrate
            - check: {equals: {the: '{{ counter }}', is: 2}}
            - run: migrate
            - check: {equals: {the: '{{ counter }}', is: 2}}
        ''')
        self.populate_file('migration.yaml', '''---
        steps:
            - echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
            - stop: 
                if: 
                    equals: '{{ counter > 1 }}'
            - echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
            - stop: 
                if: 
                    equals: '{{ counter > 1 }}'
            - echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
            - check: {equals: {the: '{{ counter }}', is: 2}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
