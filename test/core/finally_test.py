import os
from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from test.test_utils import check_file


class FinallyTest(TestClass):
    def __init__(self, method_name):
        super().__init__('finally_test', method_name)

    def test_run_finally(self):
        self.populate_file('main.yaml', '''---
        steps:
            - echo: {from: '123', to: sys_env.output}
        finally:
            - sh: 
                command: 'rm sys_env.output'
                path: '{{ CURRENT_DIR }}'
        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertFalse(check_file(join(self.test_dir, 'sys_env.output'), '123'))

    def test_run_finally_fail_fail(self):
        self.populate_file('main.yaml', '''---
                        steps:
                            - check: {equals: {the: '1', is: '2'}}
                        finally:
                            - sh: 
                                command: 'mkdir test'
                                path: '{{ CURRENT_DIR }}'
                                run_if: 'fail'
                        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertTrue(os.path.exists(join(self.test_dir, 'test')))

    def test_run_finally_fail_pass(self):
        self.populate_file('main.yaml', '''---
                        steps:
                            - check: {equals: {the: '2', is: '2'}}
                        finally:
                            - sh: 
                                command: 'mkdir test'
                                path: '{{ CURRENT_DIR }}'
                                run_if: 'fail'
                        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertFalse(os.path.exists(join(self.test_dir, 'test')))

    def test_run_finally_pass_fail(self):
        self.populate_file('main.yaml', '''---
                        steps:
                            - check: {equals: {the: '1', is: '2'}}
                        finally:
                            - sh: 
                                command: 'mkdir test'
                                path: '{{ CURRENT_DIR }}'
                                run_if: 'pass'
                        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertFalse(os.path.exists(join(self.test_dir, 'test')))

    def test_run_finally_pass_pass(self):
        self.populate_file('main.yaml', '''---
                        steps:
                            - check: {equals: {the: '2', is: '2'}}
                        finally:
                            - sh: 
                                command: 'mkdir test'
                                path: '{{ CURRENT_DIR }}'
                                run_if: 'pass'
                        ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertTrue(os.path.exists(join(self.test_dir, 'test')))

    def test_run_finally_always_pass(self):
        self.populate_file('main.yaml', '''---
                                steps:
                                    - check: {equals: {the: '2', is: '2'}}
                                finally:
                                    - sh: 
                                        command: 'mkdir test'
                                        path: '{{ CURRENT_DIR }}'
                                        run_if: 'always'
                                ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertTrue(os.path.exists(join(self.test_dir, 'test')))

    def test_run_finally_always_fail(self):
        self.populate_file('main.yaml', '''---
                                steps:
                                    - check: {equals: {the: '1', is: '2'}}
                                finally:
                                    - sh: 
                                        command: 'mkdir test'
                                        path: '{{ CURRENT_DIR }}'
                                        run_if: 'always'
                                ''')
        runner = Runner(self.test_dir,
                        join(self.test_dir, 'main.yaml'),
                        None,
                        system_environment=dict(os.environ))
        runner.run_tests()
        self.assertTrue(os.path.exists(join(self.test_dir, 'test')))
