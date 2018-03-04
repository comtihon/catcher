from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class VariablesTest(TestClass):
    def __init__(self, method_name):
        super().__init__('variables_test', method_name)

    # test computed variables available later
    def test_computed_available_later(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: 
                actions: 
                    - {from: 'hello', register: {foo: 'bar'}}
                    - {from: '{{ foo }}', to: one.output}
            
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bar'))

    # test computed available in the other step
    def test_computed_available_other_step(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: 'hello', register: {foo: 'bar'}}
            - echo: {from: '{{ foo }}', to: one.output}
            
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), 'bar'))

    # test var can be computed from the template
    def test_computed_with_template(self):
        self.populate_file('main.yaml', '''---
        variables:
            path: /home/user
            test: main.yml
        steps:
            - echo: {from: 'hello', register: {foo: '{{ path }}/{{ test }}'}}
            - echo: {from: '{{ foo }}', to: one.output}
            
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'one.output'), '/home/user/main.yml'))

