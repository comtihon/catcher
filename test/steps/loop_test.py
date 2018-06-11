from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class LoopTest(TestClass):
    def __init__(self, method_name):
        super().__init__('loop_test', method_name)

    def test_while_short(self):
        self.populate_file('main.yaml', '''---
        variables:
            counter: 0
        steps:
            - loop: 
                while:
                    if: '{{ counter < 10 }}'
                    do:
                        echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
            - check: '{{ counter == 10 }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_while_full(self):
        self.populate_file('main.yaml', '''---
        variables:
            counter: 0
        steps:
            - loop: 
                while:
                    if: 
                        equals: {the: '{{ counter }}', is_not: 10}
                    do:
                        echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
            - check: '{{ counter == 10 }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    # test if multiple actions is available and variables from previous actions is available in current one
    def test_while_multiple_actions(self):
        self.populate_file('main.yaml', '''---
        variables:
            counter: 0
        steps:
            - loop: 
                while:
                    if: '{{ counter < 10 }}'
                    do:
                        - echo: {from: '{{ result }}', to: '{{ counter }}.output'}
                        - echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}', result: '{{ OUTPUT }}'}}
            - check: '{{ counter == 10 }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, '0.output'), ''))
        for i in range(1, 10):
            self.assertTrue(check_file(join(self.test_dir, str(i) + '.output'), str(i)))

    def test_max_cycle(self):
        self.populate_file('main.yaml', '''---
        variables:
            counter: 0
        steps:
            - loop: 
                while:
                    if: 
                        equals: {the: '{{ counter }}', is_not: 10000}
                    do:
                        echo: {from: '{{ counter + 1}}', register: {counter: '{{ OUTPUT }}'}}
                    max_cycle: 10
            - check: '{{ counter == 11 }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_for(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: [1, 2, 3, 4, 5, 6]
        steps:
            - loop: 
                foreach:
                    in: '{{ list }}'
                    do:
                        echo: {from: '{{ ITEM }}', to: '{{ ITEM }}.output'}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        for i in range(1, 6):
            self.assertTrue(check_file(join(self.test_dir, str(i) + '.output'), str(i)))

    # check multiple actions are allowed, last statement's return is available.
    def test_for_multiple_actions(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: [1, 2, 3, 4, 5, 6]
        steps:
            - loop: 
                foreach:
                    in: '{{ list }}'
                    do:
                        - echo: {from: '{{ ITEM }}', register: {output: '{{ OUTPUT }}'}}
                        - echo: {from: '{{ ITEM }}', to: '{{ ITEM }}.output'}
            - check: '{{ output == 6 }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_iterate_dict(self):
        self.populate_file('main.yaml', '''---
        variables:
            list: [{'key': 'a', 'value': 1}, {'key': 'b', 'value': 2}, {'key': 'c', 'value': 3}]
        steps:
            - loop: 
                foreach:
                    in: '{{ list }}'
                    do:
                        - echo: {from: '{{ ITEM }}', register: {output: '{{ OUTPUT }}'}}
                        - echo: {from: '{{ ITEM["value"] }}', to: '{{ ITEM["key"] }}.output'}
            - check: '{{ output == {"key": "c", "value": 3} }}'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue(check_file(join(self.test_dir, 'a.output'), '1'))
        self.assertTrue(check_file(join(self.test_dir, 'b.output'), '2'))
        self.assertTrue(check_file(join(self.test_dir, 'c.output'), '3'))

    def test_loop_with_include(self):
        self.populate_file('main.yaml', '''---
        include: 
            file: print_file.yaml
            as: print
        variables:
            list: [{'file': 'a', 'value': 1}, {'file': 'b', 'value': 2}, {'file': 'c', 'value': 3}]
        steps:
            - loop: 
                foreach:
                    in: '{{ list }}'
                    do:
                        run: 
                            include: 'print'
                            variables: 
                                data: '{{ ITEM["value"] }}'
                                filename: '{{ ITEM["file"] }}'
        ''')
        self.populate_file('print_file.yaml', '''---
         steps:
            - echo: {from: '{{ data }}', to: '{{ filename }}'}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        runner.run_tests()
        self.assertTrue(check_file(join(self.test_dir, 'a'), '1'))
        self.assertTrue(check_file(join(self.test_dir, 'b'), '2'))
        self.assertTrue(check_file(join(self.test_dir, 'c'), '3'))
