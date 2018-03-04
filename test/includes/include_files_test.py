import os
from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class IncludeFilesTest(TestClass):
    def __init__(self, method_name):
        super().__init__('includes_files_test', method_name)

    # test include one file, run on include
    def test_simple_include(self):
        self.populate_file('main.yaml', '''---
        include: simple_file.yaml
        ''')
        self.populate_file('simple_file.yaml', '''---
        variables:
            foo: bar
        steps:
            - echo: {from: '{{ foo }}', to: foo.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'foo.output'), 'bar'))

    # test include one file, no run on include
    def test_dict_include(self):
        self.populate_file('main.yaml', '''---
        include: 
            file: simple_file.yaml
            run_on_include: false
        ''')
        self.populate_file('simple_file.yaml', '''---
        variables:
            foo: bar
        steps:
            - echo: {from: '{{ foo }}', to: foo.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(not os.path.exists(join(self.test_dir, 'foo.output')))

    # test include multiple files
    def test_multiple_includes(self):
        self.populate_file('main.yaml', '''---
        include: 
            - file: simple_file.yaml
              run_on_include: false
            - other_simple_file.yaml
        ''')
        self.populate_file('simple_file.yaml', '''---
        variables:
            foo: bar
        steps:
            - echo: {from: '{{ foo }}', to: foo.output}
        ''')
        self.populate_file('other_simple_file.yaml', '''---
        variables:
            foo: baz
        steps:
            - echo: {from: '{{ foo }}', to: other.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(not os.path.exists(join(self.test_dir, 'foo.output')))
        self.assertTrue(check_file(join(self.test_dir, 'other.output'), 'baz'))

    # test includes with includes
    def test_recursive_includes(self):
        self.populate_file('main.yaml', '''---
        include: 
            - simple_file.yaml
        ''')
        self.populate_file('simple_file.yaml', '''---
        include: 
            - other_simple_file.yaml
        variables:
            foo: bar
        steps:
            - echo: {from: '{{ foo }}', to: foo.output}
        ''')
        self.populate_file('other_simple_file.yaml', '''---
        variables:
            foo: baz
        steps:
            - echo: {from: '{{ foo }}', to: other.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'foo.output'), 'bar'))
        self.assertTrue(check_file(join(self.test_dir, 'other.output'), 'baz'))

    # test fail on circular includes
    def test_circular_includes(self):
        self.populate_file('main.yaml', '''---
        include: 
            - simple_file.yaml
        ''')
        self.populate_file('simple_file.yaml', '''---
        include: 
            - other_simple_file.yaml
        variables:
            foo: bar
        steps:
            - echo: {from: '{{ foo }}', to: foo.output}
        ''')
        self.populate_file('other_simple_file.yaml', '''---
        include: 
            - simple_file.yaml
        variables:
            foo: baz
        steps:
            - echo: {from: '{{ foo }}', to: other.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        try:
            runner.run_tests()
            self.fail('circular dependency not detected')
        except Exception as e:
            self.assertTrue(str(e).startswith('Circular dependencies for'))

    # test run on include and later by alias
    def test_run_on_include_and_later(self):
        self.populate_file('main.yaml', '''---
        include: 
            file: simple_file.yaml
            variables:
                file: include
            as: test
            run_on_include: true
        steps:
            - run: 
                include: test
                variables: 
                    file: other
        ''')
        self.populate_file('simple_file.yaml', '''---
        steps:
            - echo: {from: 'hello', to: '{{ file }}.output'}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'include.output'), 'hello'))
        self.assertTrue(check_file(join(self.test_dir, 'other.output'), 'hello'))
