import random
from os.path import join

import pytest
from faker import Faker

from test.abs_test_class import TestClass
from catcher.core.runner import Runner
from test.test_utils import check_file
from catcher.utils.singleton import Singleton


class FiltersTest(TestClass):
    def __init__(self, method_name):
        super().__init__('filters_test', method_name)
        Singleton._instances = {}

    def test_builtin_filters_available(self):
        self.populate_file('main.yaml', '''---
                variables:
                    my_var: test
                steps:
                    - echo: {from: '{{ "test" | hash }}', to: one.output}
                    - echo: {from: '{{ my_var | hash("sha1") }}', to: two.output}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '098f6bcd4621d373cade4e832627b4f6'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'))

    def test_builtin_functions_available(self):
        self.populate_file('main.yaml', '''---
                variables:
                    my_list: ['one', 'two', 'three']
                steps:
                    - echo: {from: '{{ random("ipv4_private") }}', to: one.output}
                    - echo: {from: '{{ random_int(1, 10) }}', to: two.output}
                    - echo: {from: '{{ random_choice(my_list) }}', to: three.output}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        Faker.seed(4321)
        random.seed(123)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '10.32.135.245'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), '1'))
        self.assertTrue(check_file(join(self.test_dir, 'three.output'), 'three'))

    def test_custom_filters_available(self):
        self.populate_file('custom_filter.py',
                           '''def filter_increment(input):
       if isinstance(input, int):
         return input + 1
       return 'not an int'
    
def filter_to_string(input, arg='test'):
  return _not_a_fun(input) + ' ' + arg

def _not_a_fun(arg):
  return 'to_str=' + str(arg)  
                            ''')
        self.populate_file('main.yaml', '''---
                        steps:
                            - echo: {from: '{{ 221 | increment }}', to: one.output}
                            - echo: {from: '{{ 221 | to_string("hello") }}', to: two.output}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None,
                        filter_list=[join(self.test_dir, 'custom_filter.py')])
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '222'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'to_str=221 hello'))

    def test_custom_functions_available(self):
        self.populate_file('custom_filter.py',
                           '''def function_my_custom():
                               return {'key': 'value'}

def function_my_other(input):
  return _not_a_fun(input)

def _not_a_fun(arg):
  return 'to_str=' + str(arg)  
                            ''')
        self.populate_file('main.yaml', '''---
                                steps:
                                    - echo: {from: '{{ my_custom() }}', to: one.output}
                                    - echo: {from: '{{ my_other("test") }}', to: two.output}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None,
                        filter_list=[join(self.test_dir, 'custom_filter.py')])
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), "{'key': 'value'}"))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'to_str=test'))

    def test_custom_both_available(self):
        self.populate_file('custom_filter.py',
                           '''def filter_increment(input):
       if isinstance(input, int):
         return input + 1
       return 'not an int'
       
def function_my_other(input):
  return _not_a_fun(input)

def _not_a_fun(arg):
  return 'to_str=' + str(arg)  
                            ''')
        self.populate_file('main.yaml', '''---
                                steps:
                                    - echo: {from: '{{ 221 | increment }}', to: one.output}
                                    - echo: {from: '{{ my_other("test") }}', to: two.output}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None,
                        filter_list=[join(self.test_dir, 'custom_filter.py')])
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '222'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'to_str=test'))

    def test_custom_ignore_other(self):
        self.populate_file('custom_filter.py',
                           '''def other(arg):
  return 'to_str=' + str(arg)  
                            ''')
        self.populate_file('main.yaml', '''---
                                steps:
                                    - echo: {from: '{{ 221 | other }}', to: one.output}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None,
                        filter_list=[join(self.test_dir, 'custom_filter.py')])
        self.assertFalse(runner.run_tests())

    @pytest.mark.skip(reason="can't catch bug with timezones. Disabled for CI.")
    def test_date_time_filters(self):
        self.populate_file('main.yaml', '''---
                                variables:
                                    date_time: '2020-03-30 11:21:47.455790'
                                    timestamp: 1585560107.45579
                                steps:
                                    - echo: {from: '{{ date_time | astimestamp }}', to: one.output}
                                    - echo: {from: '{{ timestamp | asdate }}', to: two.output}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), "1585560107.45579"))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), '2020-03-30 11:21:47.455790'))

    def test_dt_filters_compatible(self):
        """
        old (variable based) and new (function based) formats are not compatible, as variable based date format
        drops milliseconds. To make this test pass I have to add current_ts.split(".")[0]+".0" which also drops it
        """
        self.populate_file('main.yaml', '''---
                            variables:
                                current_dt: '{{ NOW_DT }}'
                                current_ts: '{{ NOW_TS }}'
                            steps:
                                - check: {equals: {the: '{{ current_dt }}', 
                                is: '{{ current_ts | asdate(date_format="%Y-%m-%dT%H:%M:%S0+0000") }}'}}
                                - check: {equals: {the: '{{ current_ts.split(".")[0]+".0" }}', 
                                is: '{{ current_dt | astimestamp(date_format="%Y-%m-%dT%H:%M:%S0+0000") }}'}}
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_dt_fitlers_revertable(self):
        self.populate_file('main.yaml', '''---
                                variables:
                                    current_ts: '{{ now_ts() }}'
                                steps:
                                    - echo: {from: '{{ current_ts | asdate }}', register: {current_dt: '{{ OUTPUT }}'}}
                                    - check: {equals: {the: '{{ current_ts }}', is: '{{ current_dt | astimestamp }}'}}
                                    - check: {equals: {the: '{{ current_dt }}', is: '{{ current_ts | asdate }}'}}
                                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_data_conversion_filters(self):
        self.populate_file('main.yaml', '''---
                        variables:
                            my_tuple: ('one', 'two', 'three')
                            my_list: ['one', 'two', 'three']
                            my_dict: {'one': 1, 'two': 2}
                            my_int: 17
                            my_float: 36.6
                        steps:
                            - check: {equals: {the: '{{ my_tuple }}', is: '{{ my_list | astuple }}'}}
                            - check: {equals: {the: '{{ my_list }}', is: '{{ my_tuple | aslist }}'}}
                            - check: {equals: {the: '{{ my_int }}', is: '{{ "17" | asint }}'}}
                            - check: {equals: {the: '{{ my_float }}', is: '{{ "36.6" | asfloat }}'}}
                            - check: {equals: {the: '{{ my_dict }}', is: '{{ [("one", 1), ("two", 2)] | asdict }}'}}
                            - check: {equals: {the: [2, 2], 
                                                is: '{{ ([("a", 2), ("b", 2)] | asdict).values() |aslist }}'}}
                            - check: {equals: {the: '17', is: '{{ my_int | asstr }}'}}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # hash function is properly called
    def test_hash(self):
        self.populate_file('main.yaml', '''---
        variables:
            my_var: test
        steps:
            - echo: {from: '{{ "test" | hash("sha1") }}', to: one.output}
            - echo: {from: '{{ my_var | hash("sha1") }}', to: two.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'))

    # random choice on a list can be called
    def test_random_choice(self):
        self.populate_file('main.yaml', '''---
        variables:
            my_list: ['one', 'two', 'three']
        steps:
            - echo: {from: '{{ random_choice(my_list) }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        random.seed(123)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'three'))

    # random int with args can be called
    def test_random_int(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ random_int(1, 10) }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        random.seed(123)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '9'))

        # no upper limit
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ random_int(1) }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        random.seed(123)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '5186474716495645053'))

        # no lower limit
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ random_int(range_to=1) }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        random.seed(123)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '-2936754363331581815'))

    # faker can be called from catcher
    def test_random_functions(self):
        Faker.seed(4321)
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '{{ random("ipv4_private") }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '10.32.135.245'))
