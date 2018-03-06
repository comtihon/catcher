from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class ChecksTest(TestClass):
    def __init__(self, method_name):
        super().__init__('checks_test', method_name)

    # test computed var equals constant value
    def test_computed_equals_constant(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'hello', register: {'foo': 'value'}}
            - check: {the: '{{ foo }}', equals: 'value'}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test computed var equals other var
    def test_computed_equals_variable(self):
        self.populate_file('main.yaml', '''---
        variables:
            foo: bar
            foo2: bar
        steps:
            - echo: {from: '{{ foo }}'}
            - check: {the: 'bar', equals: '{{ foo }}'}
            - check: {the: '{{ foo }}', equals: 'bar'}
            - check: {the: '{{ foo }}', equals: '{{ foo2 }}'}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test if any of the list's elements is equal to var
    def test_any_equal(self):
        self.populate_file('main.yaml', '''---
        variables:
            foo: [bar, baz]
        steps:
            - echo: {from: '{{ foo }}'}
            - check: 
                the: '{{ foo }}'
                any:
                    equals: 'baz'
            - check: 
                the: [bar, baz]
                any:
                    equals: 'baz'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test if all of the list's elements is equal to var
    def test_all_equal(self):
        self.populate_file('main.yaml', '''---
        variables:
            foo: [1, 1]
        steps:
            - echo: {from: '{{ foo }}'}
            - check: 
                the: '{{ foo }}'
                all:
                    equals: 1
            - check: 
                the: [1, 1]
                all:
                    equals: 1
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())


