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

    # test if `contains` work with list/dict
    def test_contains(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: ['a', 'b', 'c']
            dict: {'a': 1, 'b': 2, 'c': 3}
        steps:
            - check: 
                the: '{{ list }}'
                contains: 'a'
            - check: 
                the: '{{ dict }}'
                contains: 'a'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test if `or` works
    def test_or(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: ['a', 'b', 'c']
        steps:
            - check: 
                the: '{{ list }}'
                or: 
                    - contains: '1'
                    - equals: {the: '{{ list[0] }}', equals: 'a'}
                    - contains: 'b'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test if `and` works
    def test_and(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: ['a', 'b', 3]
        steps:
            - check: 
                the: '{{ list }}'
                and: 
                    - contains: 'a'
                    - equals: {the: '{{ list[1] }}', equals: 'b'}
                    - equals: {the: '{{ list[2] > 2 }}', equals: true}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test if inverted operators work
    def test_negative(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: ['d', 'c', 1]
        steps:
            - check: 
                the: '{{ list }}'
                and: 
                    - not_contains: 'a'
                    - equals: {the: '{{ list[1] }}', not_equals: 'b'}
                    - not_equals: {the: '{{ list[2] > 2 }}', equals: true}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())