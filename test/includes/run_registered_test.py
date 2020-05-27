from os.path import join

import os

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class RunRegisteredIncludeTest(TestClass):
    def __init__(self, method_name):
        super().__init__('run_registered_includes_test', method_name)

    # test register include and run later
    def test_simple_include(self):
        self.populate_file('main.yaml', '''---
        include: 
            file: simple_file.yaml
            as: simple
            run_on_include: false
        steps:
            - run: 'simple'
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

    # test register include and run only selected tag
    def test_register_run_tags(self):
        self.populate_file('main.yaml', '''---
        include: 
            file: simple_file.yaml
            as: simple
        steps:
            - run: 'simple.one'
        ''')
        self.populate_file('simple_file.yaml', '''---
        variables:
            foo: 1
            baz: 2
            bar: 3
        steps:
            - echo: {from: '{{ foo }}', to: foo.output, tag: one}
            - echo: {from: '{{ baz }}', to: baz.output}
            - echo: {from: '{{ bar }}', to: bar.output, tag: one}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'foo.output'), '1'))
        self.assertTrue(not os.path.exists(join(self.test_dir, 'baz.output')))
        self.assertTrue(check_file(join(self.test_dir, 'bar.output'), '3'))

    # test register include and run only selected tag (long form), include name with dot
    def test_register_run_tags_with_dot(self):
        self.populate_file('main.yaml', '''---
        include: 
            file: simple_file.yaml
            as: simple.with_dot
        steps:
            - run: 
                include: 'simple.with_dot.one'
        ''')
        self.populate_file('simple_file.yaml', '''---
        variables:
            foo: 1
            baz: 2
            bar: 3
        steps:
            - echo: {from: '{{ foo }}', to: foo.output, tag: one}
            - echo: {from: '{{ baz }}', to: baz.output}
            - echo: {from: '{{ bar }}', to: bar.output, tag: one}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'foo.output'), '1'))
        self.assertTrue(not os.path.exists(join(self.test_dir, 'baz.output')))
        self.assertTrue(check_file(join(self.test_dir, 'bar.output'), '3'))

    # test include can be run from variable
    def test_run_from_template(self):
        self.populate_file('main.yaml', '''---
        include: 
            - file: one.yaml
              as: one
            - file: two.yaml
              as: two
            - file: determine_include.yaml
              as: determine_include
        steps:
            - run: 'determine_include'
            - run: '{{ include }}'
        ''')
        self.populate_file('one.yaml', '''---
        steps:
            - echo: {from: 'bar', to: foo.output}
        ''')
        self.populate_file('two.yaml', '''---
        steps:
            - echo: {from: 'baz', to: foo.output}
        ''')
        self.populate_file('determine_include.yaml', '''---
        steps:
            - echo: {from: 'hello', register: {include: one}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'foo.output'), 'bar'))
        self.assertTrue(not os.path.exists(join(self.test_dir, 'baz.output')))

    # run tagged include which runs untagged include
    def test_run_tagged_untagged(self):
        self.populate_file('main.yaml', '''---
                include: 
                    file: one.yaml
                    as: one
                steps:
                    - run: 'one.before'
                ''')
        self.populate_file('one.yaml', '''---
                include: 
                    file: two.yaml
                    as: two
                steps:
                    - run:
                        include: two
                        tag: before
                    - echo: {from: '{{ bar }}', to: after.output, tag: after}
                ''')
        self.populate_file('two.yaml', '''---
                steps:
                    - echo: {from: '1', to: foo.output}
                    - echo: {from: '2', to: baz.output}
                    - echo: {from: '3', to: bar.output}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'foo.output'), '1'))
        self.assertTrue(check_file(join(self.test_dir, 'baz.output'), '2'))
        self.assertTrue(check_file(join(self.test_dir, 'bar.output'), '3'))

    # run tagged include which runs tagged include
    def test_run_tagged_tagged(self):
        self.populate_file('main.yaml', '''---
                        include: 
                            file: one.yaml
                            as: one
                        steps:
                            - run: 'one.before'
                        ''')
        self.populate_file('one.yaml', '''---
                        include: 
                            file: two.yaml
                            as: two
                        steps:
                            - run:
                                include: two.one
                                tag: before
                            - echo: {from: '{{ bar }}', to: after.output, tag: after}
                        ''')
        self.populate_file('two.yaml', '''---
                        steps:
                            - echo: {from: '1', to: foo.output, tag: one}
                            - echo: {from: '2', to: baz.output, tag: two}
                            - echo: {from: '3', to: bar.output, tag: three}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'foo.output'), '1'))
        self.assertTrue(not os.path.exists(join(self.test_dir, 'baz.output')))
        self.assertTrue(not os.path.exists(join(self.test_dir, 'bar.output')))
