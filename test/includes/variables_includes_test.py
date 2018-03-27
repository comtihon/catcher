from os.path import join

from catcher.utils.file_utils import read_file

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class IncludeFilesTest(TestClass):
    def __init__(self, method_name):
        super().__init__('includes_files_test', method_name)

    # test variables from one include is available in another
    def test_vars_available_got(self):
        self.populate_file('main.yaml', '''---
        include: 
            - one.yaml
            - two.yaml
        ''')
        self.populate_file('one.yaml', '''---
        variables:
            foo: bar
        steps:
            - echo: {from: '{{ foo }}', to: one.output}
        ''')
        self.populate_file('two.yaml', '''---
        steps:
            - echo: {from: '{{ foo }}', to: two.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bar'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'bar'))

    # test variables in include statement override file's and got variables
    def test_vars_override_manual(self):
        self.populate_file('main.yaml', '''---
        include: 
            - one.yaml
            - file: two.yaml
              variables:
                one: override1
                two: override2
        ''')
        self.populate_file('one.yaml', '''---
        variables:
            one: foo
        steps:
            - echo: {from: 'hello'}
        ''')
        self.populate_file('two.yaml', '''---
        variables:
            two: bar
        steps:
            - echo: 
                actions: 
                    - {from: '{{ one }}', to: one.output}
                    - {from: '{{ two }}', to: two.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'override1'))
        self.assertTrue(check_file(join(self.test_dir, 'two.output'), 'override2'))

    # test variables in file override got variables
    def test_vars_override_file(self):
        self.populate_file('main.yaml', '''---
        include: 
            - one.yaml
            - two.yaml
        ''')
        self.populate_file('one.yaml', '''---
        variables:
            foo: bar
        steps:
            - echo: {from: 'hello'}
        ''')
        self.populate_file('two.yaml', '''---
        variables:
            foo: baz
        steps:
            - echo: {from: '{{ foo }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'baz'))

    # test computed variables available in another
    def test_vars_available_computed(self):
        self.populate_file('main.yaml', '''---
        include: 
            - one.yaml
            - two.yaml
        ''')
        self.populate_file('one.yaml', '''---
        steps:
            - echo: {from: 'hello', register: {foo: 'bar'}}
            
        ''')
        self.populate_file('two.yaml', '''---
        steps:
            - echo: {from: '{{ foo }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bar'))

    # test variables in include statement override computed
    def test_vars_override_computed(self):
        self.populate_file('main.yaml', '''---
        include: 
            - one.yaml
            - file: two.yaml
              variables: 
                foo: baz
        ''')
        self.populate_file('one.yaml', '''---
        steps:
            - echo: {from: 'hello', register: {foo: 'bar'}}
            
        ''')
        self.populate_file('two.yaml', '''---
        steps:
            - echo: {from: '{{ foo }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'baz'))

    # test if variables, pass to includes are filled in
    def test_vars_included_filled_in(self):
        self.populate_file('main.yaml', '''---
        include: 
            - file: one.yaml
              as: one
        steps:
            - echo: {from: '{{ RANDOM_STR }}', to: main.output, register: {uuid: '{{ OUTPUT }}'}}
            - run: 
                include: one
                variables: 
                    id: '{{ uuid }}'
        ''')
        self.populate_file('one.yaml', '''---
        steps:
            - echo: {from: '{{ id }}', to: one.output}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        main = read_file(join(self.test_dir, 'main.output'))
        one = read_file(join(self.test_dir, 'one.output'))
        self.assertEqual(main, one)
        self.assertTrue(one)
