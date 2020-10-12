from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class ChecksTest(TestClass):
    def __init__(self, method_name):
        super().__init__('checks_test', method_name)

    def setUp(self):
        super().setUp()

    # test read file with echo
    def test_read_file(self):
        self.populate_resource('debug.input', '123')
        self.populate_file('main.yaml', '''---
        variables:
            foo: true
        steps:
            - echo: {from_file: debug.input, register: {user_email: '{{ OUTPUT }}'}}
            - check: {equals: {the: '{{ user_email }}', is: '123'}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test echo to file
    def test_write_file(self):
        self.populate_file('main.yaml', '''---
                variables:
                    user_email: 123
                steps:
                    - echo: {from: '{{ user_email }}', to: 'debug.output'}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'debug.output'), '123'))

    # test write to a variable
    def test_write_variable(self):
        self.populate_file('main.yaml', '''---
                        variables:
                            user_email: 123
                        steps:
                            - echo: {from: '{{ user_email }}', register: {'foo': '{{ OUTPUT }}'} }
                            - check: {equals: {the: '{{ foo }}', is: '123'}}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_read_write_to_file_template(self):
        self.populate_resource('foo/baz/bar.json', '123')
        self.populate_file('main.yaml', '''---
                        variables:
                            filename: foo/baz/bar.json
                        steps:
                            - echo: {from_file: '{{ filename }}', to: 'resources/{{ filename.replace("/baz/", "/bar/")}}'}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'resources/foo/bar/bar.json'), '123'))