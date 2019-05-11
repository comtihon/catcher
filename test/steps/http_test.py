from os.path import join

import requests_mock

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class HttpTest(TestClass):
    def __init__(self, method_name):
        super().__init__('http', method_name)

    @requests_mock.mock()
    def test_status_code_get(self, m):
        m.get('http://test.com', status_code=500)
        self.populate_file('main.yaml', '''---
            steps:
                - http: {get: {url: 'http://test.com', response_code: 200}}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertFalse(runner.run_tests())

    @requests_mock.mock()
    def test_status_code_ok(self, m):
        m.get('http://test.com', status_code=200)
        self.populate_file('main.yaml', '''---
            steps:
                - http: {get: {url: 'http://test.com', response_code: 200}}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @requests_mock.mock()
    def test_get_response(self, m):
        m.get('http://test.com', json={'uuid': 'qwerty', 'checked': True})
        self.populate_file('main.yaml', '''---
            steps:
                - http: 
                    get: 
                        url: 'http://test.com'
                        response_code: 200
                    register: {checked: '{{ OUTPUT.checked }}'}
                - check: '{{ checked }}'
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @requests_mock.mock()
    def test_post_response(self, m):
        m.post('http://test.com', text='Error message: no such id')
        self.populate_file('main.yaml', '''---
            steps:
                - http: 
                    post: 
                        url: 'http://test.com'
                        body: {'id': 1234, 'action': 'fee'}
                    register: {reply: '{{ OUTPUT }}'}
                - check:
                    contains: {'the': 'Error', in: '{{ reply }}'}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @requests_mock.mock()
    def test_post_with_vars(self, m):
        m.post('http://test.com', json={'id': 1234, 'action': 'fee'})
        self.populate_file('main.yaml', '''---
            variables:
                id: 1234
            steps:
                - http: 
                    post: 
                        url: 'http://test.com'
                        body: {'id': '{{ id }}', 'action': 'fee'}
                    register: {reply: '{{ OUTPUT.id }}'}
                - check:
                    equals: {the: '{{ reply }}', is: '{{ id }}'}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @requests_mock.mock()
    def test_post_from_file(self, m):
        m.post('http://test.com', text="loaded ok")
        self.populate_file('answers.json', '''
        {
            "answers":[
                {"id": 1,"response": true},
                {"id": 2,"response": false},
                {"id": 3,"response": true},
                {"id": 4,"response": false},
                {"id": 5,"response": true}
            ]
        }
        ''')

        self.populate_file('main.yaml', '''---
            steps:
                - http: 
                    post: 
                        url: 'http://test.com'
                        body_from_file: "'''
                           + join(self.test_dir, 'answers.json') + '''"
                    register: {reply: '{{ OUTPUT }}'}
                - check:
                    equals: {the: '{{ reply }}', is: 'loaded ok'}
            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    def test_should_fail(self):
        self.populate_file('main.yaml', '''---
                    steps:
                        - http: 
                            get: 
                                url: 'http://undefined'
                                should_fail: true
                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
