from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class ChecksTest(TestClass):
    def __init__(self, method_name):
        super().__init__('checks_test', method_name)

    # test simple equals
    def test_check_short_form(self):
        self.populate_file('main.yaml', '''---
        variables:
            foo: true
        steps:
            - check: '{{ foo }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test computed var equals constant value
    def test_computed_equals_constant(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'hello', register: {'foo': 'value'}}
            - check: {equals: {the: '{{ foo }}', is: 'value'}}
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
            - check: {equals: {the: 'bar', is: '{{ foo }}'}}
            - check: {equals: {the: '{{ foo }}', is: 'bar'}}
            - check: {equals: {the: '{{ foo2 }}', is: '{{ foo }}'}}
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
                any:
                    of: '{{ foo }}'
                    equals: 'baz'
            - check: 
                any:
                    of: [bar, baz]
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
                all:
                    of: '{{ foo }}'
                    equals: 1
            - check: 
                all: 
                    of: [1,1]
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
                contains: {the: 'a', in: '{{ list }}'}
            - check: 
                contains: {the: 'a', in: '{{ dict }}'}
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
                or: 
                    - contains: {the: '1', in: '{{ list }}'}
                    - equals: {the: '{{ list[0] }}', is: 'a'}
                    - contains: {the: 'b', in: '{{ list }}'}
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
                and: 
                    - contains: {the: 'a', in: '{{ list }}'}
                    - equals: {the: '{{ list[1] }}', is: 'b'}
                    - equals: {the: '{{ list[2] > 2 }}', is: true}
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
                and: 
                    - contains: {the: 'a', not_in: '{{ list }}'}
                    - equals: {the: '{{ list[1] }}', is_not: 'b'}
                    - equals: {the: '{{ list[2] > 2 }}', is_not: true}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test if ITEM is available in list
    def test_items_iteration(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: [{n: 1, k: 'a'}, {n: 2, k: 'a'}, {n: 3, k: 'a'}]
        steps:
            - check: 
                all:
                    of: '{{ list }}'
                    equals: {the: '{{ ITEM.k }}', is: 'a'}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())