from os.path import join

import requests_mock

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

    # all level of templates should be resolved when including variables
    def test_template_in_template(self):
        self.populate_file('main.yaml', '''---
                variables:
                    bar: '{{ RANDOM_STR }}'
                include: 
                    - file: one.yaml
                      as: one
                steps:
                    - echo: {from: '{{ bar }}', to: main.output}
                    - run: one
                ''')
        self.populate_file('one.yaml', '''---
                variables:
                    foo: '{{ bar }}'
                include: 
                    - file: two.yaml
                      as: two
                steps:
                    - echo: {from: '{{ foo }}', to: one.output}
                    - run: two
                ''')
        self.populate_file('two.yaml', '''---
                variables:
                    final: '{{ foo }}'
                steps:
                    - echo: {from: '{{ final }}', to: two.output}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        main = read_file(join(self.test_dir, 'main.output'))
        one = read_file(join(self.test_dir, 'one.output'))
        two = read_file(join(self.test_dir, 'two.output'))
        self.assertEqual(main, one)
        self.assertEqual(main, two)

    # all level of templates in resources should be resolved
    @requests_mock.mock()
    def test_template_in_template_resource(self, m):
        self.populate_file('main.yaml', '''---
                        variables:
                            bar: '{{ RANDOM_STR }}'
                        include: 
                            - file: one.yaml
                              as: one
                        steps:
                            - echo: {from: '{{ bar }}', to: main.output}
                            - run: one
                        ''')
        self.populate_file('one.yaml', '''---
                        variables:
                            foo: '{{ bar }}'
                        steps:
                            - http: 
                                post: 
                                    url: 'http://test.com'
                                    files:
                                        file: 'foo.json'
                        ''')
        self.populate_resource('foo.json', "{\"key\":\"{{ foo }}\"}")
        adapter = m.post('http://test.com')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        main = read_file(join(self.test_dir, 'main.output'))
        self.assertTrue("{\"key\":\"" + main + "\"}" in adapter.last_request.text)

    # predefined variable from include should be available in test already filled in,
    def test_variables_registered_in_include(self):
        self.populate_file('main.yaml', '''---
                include: 
                    - file: one.yaml
                      as: one
                steps:
                    - run: one
                    - echo: {from: '{{ generated_email }}', to: two.output}
                ''')

        self.populate_file('one.yaml', '''---
                variables:
                    generated_email: '{{ random("email") }}'
                steps:
                    - echo: {from: '{{ generated_email }}', to: one.output}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        two = read_file(join(self.test_dir, 'two.output'))
        one = read_file(join(self.test_dir, 'one.output'))
        self.assertEqual(two, one)
        self.assertNotEqual('{{ random("email") }}', one)
