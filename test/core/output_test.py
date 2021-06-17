import json
from os import listdir
from os.path import join, isfile

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class OutputTest(TestClass):
    def __init__(self, method_name):
        super().__init__('output_test', method_name)

    def test_run_multiple_steps(self):
        self.populate_file('main.yaml', '''---
        variables:
            foo: [bar, baz]
        steps:
            - echo: {from: '{{ foo }}'}
            - check: 
                any:
                    of: '{{ foo }}'
                    equals: 'baz'
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(1, len(obj))
            report = obj[0]
            self.assertEqual('test', report['type'])
            self.assertEqual(join(self.test_dir, 'main.yaml'), report['file'])
            output = report['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual(4, len(steps))  # 4 step entry for 2 steps (before & after)
            self.assertEqual('echo', list(steps[0]['step'].keys())[0])
            self.assertTrue(steps[1]['success'])
            self.assertEqual('check', list(steps[2]['step'].keys())[0])
            self.assertTrue(steps[3]['success'])
            self.assertEqual('OK', report['status'])

    def test_step_failed(self):
        self.populate_file('main.yaml', '''---
                variables:
                    foo: [bar]
                steps:
                    - echo: {from: '{{ foo }}'}
                    - check: 
                        any:
                            of: '{{ foo }}'
                            equals: '404'
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertFalse(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(1, len(obj))
            report = obj[0]
            self.assertEqual('test', report['type'])
            self.assertEqual(join(self.test_dir, 'main.yaml'), report['file'])
            output = report['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual(4, len(steps))  # 4 step entry for 2 steps (before & after)
            self.assertEqual('echo', list(steps[0]['step'].keys())[0])
            self.assertTrue(steps[1]['success'])
            self.assertEqual('check', list(steps[2]['step'].keys())[0])
            self.assertFalse(steps[3]['success'])
            self.assertTrue(self._compare_operations(steps[3]['output'],
                                                     "operation {'any': {'of': '['bar']', 'equals': '404'}} failed",
                                                     "operation {'any': {'equals': '404', 'of': '['bar']'}} failed"))
            self.assertTrue(self._compare_operations(report['status'],
                                                     "operation {'any': {'of': '['bar']', 'equals': '404'}} failed",
                                                     "operation {'any': {'equals': '404', 'of': '['bar']'}} failed"))

    def test_register_variable(self):
        self.populate_file('main.yaml', '''---
                        steps:
                            - echo: {from: 'val', register: {user: '{{ OUTPUT }}'}}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(1, len(obj))
            report = obj[0]
            self.assertEqual('test', report['type'])
            self.assertEqual(join(self.test_dir, 'main.yaml'), report['file'])
            output = report['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual(2, len(steps))  # 2 step entry for 1 step (before & after)
            self.assertEqual('echo', list(steps[0]['step'].keys())[0])
            self.assertEqual(sorted(['CURRENT_DIR', 'RESOURCES_DIR', 'TEST_NAME']),
                             sorted(list(steps[0]['variables'].keys())))
            self.assertEqual('echo', list(steps[1]['step'].keys())[0])
            self.assertEqual(sorted(['CURRENT_DIR', 'RESOURCES_DIR', 'TEST_NAME', 'user']),
                             sorted(list(steps[1]['variables'].keys())))
            self.assertEqual('val', steps[1]['variables']['user'])

    def test_run_multiple_tests(self):
        self.populate_file('first.yaml', '''---
                            steps:
                                - echo: {from: '1', register: {test: '{{ OUTPUT }}'}}
                            ''')
        self.populate_file('second.yaml', '''---
                           steps:
                               - echo: {from: '2', register: {test: '{{ OUTPUT }}'}}
                           ''')
        runner = Runner(self.test_dir, self.test_dir, None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = sorted(json.load(fp), key=lambda r: r['file'])
            self.assertEqual(2, len(obj))
            report = obj[0]
            self.assertEqual(join(self.test_dir, 'first.yaml'), report['file'])
            output = report['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual(sorted(['CURRENT_DIR', 'RESOURCES_DIR', 'TEST_NAME']),
                             sorted(list(steps[0]['variables'].keys())))
            self.assertEqual(1, steps[1]['variables']['test'])
            report = obj[1]
            self.assertEqual(join(self.test_dir, 'second.yaml'), report['file'])
            output = report['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual(sorted(['CURRENT_DIR', 'RESOURCES_DIR', 'TEST_NAME']),
                             sorted(list(steps[0]['variables'].keys())))
            self.assertEqual(2, steps[1]['variables']['test'])

    def test_run_with_include(self):
        self.populate_file('main.yaml', '''---
                include: simple_file.yaml
                steps:
                    - echo: 'hello'
                ''')
        self.populate_file('simple_file.yaml', '''---
                variables:
                    foo: bar
                steps:
                    - echo: {from: '{{ foo }}', to: foo.output}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(2, len(obj))
            report = obj[0]
            self.assertEqual('include', report['type'])
            self.assertEqual(join(self.test_dir, 'simple_file.yaml'), report['file'])
            output = report['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual(2, len(steps))
            self.assertEqual('OK', report['status'])
            report = obj[1]
            self.assertEqual('test', report['type'])
            self.assertEqual(join(self.test_dir, 'main.yaml'), report['file'])
            output = report['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual(2, len(steps))
            self.assertEqual('OK', report['status'])

    def test_run_multiple_includes(self):
        self.populate_file('main.yaml', '''---
                        include: 
                            - one.yaml
                            - two.yaml
                        steps:
                            - echo: 'hello'
                        ''')
        self.populate_file('one.yaml', '''---
                        variables:
                            foo: bar
                        steps:
                            - echo: {from: '{{ foo }}', to: one.output}
                        ''')
        self.populate_file('two.yaml', '''---
                            variables:
                                foo: bar
                            steps:
                                - echo: {from: '{{ foo }}', to: two.output}
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(3, len(obj))
            report = obj[0]
            self.assertEqual('include', report['type'])
            self.assertEqual(join(self.test_dir, 'one.yaml'), report['file'])
            report = obj[1]
            self.assertEqual('include', report['type'])
            self.assertEqual(join(self.test_dir, 'two.yaml'), report['file'])
            report = obj[2]
            self.assertEqual('test', report['type'])
            self.assertEqual(join(self.test_dir, 'main.yaml'), report['file'])

    def test_run_with_include_named(self):
        self.populate_file('main.yaml', '''---
                include: 
                    file: simple_file.yaml
                    as: simple
                    run_on_include: false
                steps:
                    - echo: 'hello'
                    - run: 'simple'
                    - echo: 'world'
                ''')
        self.populate_file('simple_file.yaml', '''---
                variables:
                    foo: bar
                steps:
                    - echo: {from: '{{ foo }}', to: foo.output}
                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(1, len(obj))
            output = obj[0]['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual('echo', list(steps[0]['step'].keys())[0])
            self.assertEqual('echo', list(steps[1]['step'].keys())[0])
            self.assertEqual('run', list(steps[2]['step'].keys())[0])
            self.assertEqual('echo', list(steps[3]['step'].keys())[0])
            self.assertEqual('echo', list(steps[4]['step'].keys())[0])
            self.assertEqual('run', list(steps[5]['step'].keys())[0])
            self.assertEqual('echo', list(steps[6]['step'].keys())[0])
            self.assertEqual('echo', list(steps[7]['step'].keys())[0])

    def test_recursive_render_dict(self):
        self.populate_file('main.yaml', '''---
                        steps:
                          - wait:                                                                                                                                                                                                                
                                name: 'Waiting for postgres'                                                                                                                                                                                               
                                seconds: 30                                                                                                                                                                                                                
                                for:                                                                                                                                                                                                                 
                                  echo: {from: '1', to: foo.output}
                        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(1, len(obj))
            output = obj[0]['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual('wait', list(steps[0]['step'].keys())[0])
            self.assertEqual('echo', list(steps[0]['step']['wait']['for'].keys())[0])

    def test_recursive_render_list(self):
        self.populate_file('main.yaml', '''---
                                steps:
                                  - wait:                                                                                                                                                                                                                
                                        name: 'Waiting for postgres'                                                                                                                                                                                               
                                        seconds: 30                                                                                                                                                                                                                
                                        for:                                                                                                                                                                                                                 
                                          - echo: {from: '1', to: foo.output}
                                          - echo: {from: '2', to: foo.output}
                                ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, output_format='json')
        self.assertTrue(runner.run_tests())
        reports = [f for f in listdir(join(self.test_dir, 'reports'))
                   if isfile(join(self.test_dir, 'reports', f)) and f.startswith('report')]
        self.assertEqual(1, len(reports))
        with open(join(self.test_dir, 'reports', reports[0]), 'r') as fp:
            obj = json.load(fp)
            self.assertEqual(1, len(obj))
            output = obj[0]['output']
            steps = [o for o in output if 'step' in o]
            self.assertEqual('wait', list(steps[0]['step'].keys())[0])
            self.assertEqual('echo', list(steps[0]['step']['wait']['for'][0].keys())[0])
            self.assertEqual('echo', list(steps[0]['step']['wait']['for'][1].keys())[0])


    # py36 has dict insert ordering, while older implementations have some other.
    @staticmethod
    def _compare_operations(operation, *expectations):
        return any([operation == exp for exp in expectations])
