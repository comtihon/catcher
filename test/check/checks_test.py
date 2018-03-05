from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


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
