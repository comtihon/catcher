import os
from os.path import join

import requests_mock

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class ComposeTest(TestClass):
    def __init__(self, method_name):
        super().__init__('compose', method_name)

    def setUp(self):
        super().setUp()
        os.makedirs(join(self.test_dir, 'resources'))

    @requests_mock.mock()
    def test_no_compose(self, m):
        m.get('http://test.com', status_code=500)
        self.populate_file('main.yaml', '''---
                    steps:
                        - http: {get: {url: 'http://test.com', response_code: 200}}
                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertFalse(runner.run_tests())

    def test_compose(self):
        self.populate_file('resources/docker-compose.yml', '''
        version: '3.1'
        services:
            mockserver:
                image: jamesdbloom/mockserver
                ports:
                - "8000:1080"
        ''')
        self.populate_file('main.yaml', '''---
                            steps:
                                 - wait:
                                    seconds: 5
                                    for:
                                        http:
                                            put:
                                                url: 'http://localhost:8000/mockserver/expectation'
                                                body:
                                                    httpRequest: {'path': '/some/path'}
                                                    httpResponse: {'body': 'hello world'}
                                                response_code: 201
                                - http: 
                                    get: 
                                        url: 'http://localhost:8000/mockserver/expectation',
                                        response_code: 200
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None,
                        resources=join(self.test_dir, 'resources'))
        self.assertFalse(runner.run_tests())
