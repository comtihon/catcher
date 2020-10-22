from contextlib import ContextDecorator
from os.path import join
from shutil import copyfile

import test
from catcher.core.runner import Runner
from test.abs_test_class import TestClass
from catcher.utils import module_utils
from catcher.utils import file_utils


class grpc_server(ContextDecorator):
    def __init__(self, server) -> None:
        super().__init__()
        self.server = server

    def __enter__(self):
        resources = join(test.get_test_dir('grpc'), 'private_resource')
        mod = module_utils.load_external_actions(join(resources, self.server))
        self.server = mod.server
        self.server.start()
        return self

    def __exit__(self, *exc):
        self.server.stop(0)
        return False


class GRPCTest(TestClass):
    def __init__(self, method_name):
        super().__init__('grpc', method_name)

    def setUp(self):
        super().setUp()
        file_utils.ensure_empty(join(test.get_test_dir(self.test_name), 'private_resource'))
        self.copy_resource('calculator.py')
        self.copy_resource('calculator.proto')
        self.copy_resource('greeter.py')
        self.copy_resource('greeter.proto')
        from grpc.tools import command
        command.build_package_protos(join(test.get_test_dir(self.test_name), 'private_resource'), strict_mode=True)

    def copy_resource(self, resource_name):
        # copy in private non-resource dir instead
        copyfile(join(self.global_resource_dir, resource_name),
                 join(join(test.get_test_dir(self.test_name), 'private_resource'), resource_name))

    @grpc_server('calculator.py')
    def test_call_simple(self):
        TestClass.copy_resource(self, 'calculator.proto')
        self.populate_file('main.yaml', '''---
                    variables:
                        my_value: 4
                    steps:
                        - wait:
                            seconds: 5
                            for:
                                - grpc:
                                    call:
                                        url: 'localhost:50051'
                                        function: calculator.squareroot
                                        schema: 'calculator.proto'
                                        data: {'value': '{{ my_value }}'}
                                    register: {value: '{{ OUTPUT.value }}'}
                        - check: 
                            equals: {'the': '{{ value }}', 'is': 2.0}
                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @grpc_server('greeter.py')
    def test_call_complex(self):
        TestClass.copy_resource(self, 'greeter.proto')
        self.populate_file('main.yaml', '''---
                            steps:
                                - wait:
                                    seconds: 5
                                    for:
                                        - grpc:
                                            call:
                                                url: 'localhost:50051'
                                                function: greeter.greet
                                                schema: 'greeter.proto'
                                                data: 
                                                    result:
                                                        url: '{{ my_url }}'
                                                        title: 'test'
                                                        snippets: 'test2'
                                            register: {value: '{{ OUTPUT.name }}'}
                                - check: 
                                    equals: {'the': '{{ value }}', 'is': 'Result for test contains test2'}
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @grpc_server('greeter.py')
    def test_call_variables(self):
        TestClass.copy_resource(self, 'greeter.proto')
        self.populate_file('main.yaml', '''---
                            variables:
                                data:
                                    result: 
                                        url: 'my'
                                        title: 'test'
                                        snippets: 'test2'
                            steps:
                                - wait:
                                    seconds: 5
                                    for:
                                        - grpc:
                                            call:
                                                url: 'localhost:50051'
                                                function: greeter.greet
                                                schema: 'greeter.proto'
                                                data: '{{ data }}'
                                            register: {value: '{{ OUTPUT.name }}'}
                                - check: 
                                    equals: {'the': '{{ value }}', 'is': 'Result for test contains test2'}
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
