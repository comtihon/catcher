from os.path import join

import pytest
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

    @requests_mock.mock()
    def test_await_2xx(self, m):
        m.get('http://test.com', status_code=201)
        self.populate_file('main.yaml', '''---
                    steps:
                        - http: {get: {url: 'http://test.com', response_code: 2xx}}
                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @requests_mock.mock()
    def test_await_range(self, m):
        m.get('http://test.com', status_code=201)
        self.populate_file('main.yaml', '''---
                            steps:
                                - http: {get: {url: 'http://test.com', response_code: 200-300}}
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @requests_mock.mock()
    def test_await_range_xx(self, m):
        m.get('http://test.com', status_code=201)
        self.populate_file('main.yaml', '''---
                                    steps:
                                        - http: {get: {url: 'http://test.com', response_code: 2xx-3xx}}
                                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @requests_mock.mock()
    def test_send_json_via_headers(self, m):
        adapter = m.post('http://test.com')

        self.populate_file('main.yaml', '''---
                                    variables:
                                        body: {'foo': 'bar'}
                                    steps:
                                        - http: 
                                            post: 
                                                url: 'http://test.com'
                                                headers: {Content-Type: 'application/json'}
                                                body: '{{ body }}'
                                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertEqual({'foo': 'bar'}, adapter.last_request.json())

    @requests_mock.mock()
    def test_send_json_directly(self, m):
        adapter = m.post('http://test.com')

        self.populate_file('main.yaml', '''---
                                    variables:
                                        body: {'foo': 'bar'}
                                    steps:
                                        - http: 
                                            post: 
                                                url: 'http://test.com'
                                                body: '{{ body |tojson }}'
                                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertEqual({'foo': 'bar'}, adapter.last_request.json())

    @requests_mock.mock()
    def test_upload_file(self, m):
        self.populate_file('main.yaml', '''---
                                    steps:
                                        - http: 
                                            post: 
                                                url: 'http://test.com'
                                                files:
                                                    file: 'foo.csv'
                                                    type: 'text/csv'
                                    ''')
        self.populate_resource('foo.csv', "one,two\n"
                                          "three,four"
                               )

        adapter = m.post('http://test.com')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue('Content-Type: text/csv' in adapter.last_request.text)
        self.assertTrue("one,two\n"
                        "three,four" in adapter.last_request.text)

    @requests_mock.mock()
    def test_upload_multiple(self, m):
        self.populate_file('main.yaml', '''---
                                    steps:
                                        - http: 
                                            post: 
                                                url: 'http://test.com'
                                                files:
                                                    - file1: 'one.json'
                                                      type: 'application/json'
                                                    - file2: 'foo.csv'
                                                      type: 'text/csv'
                                    ''')
        self.populate_resource('one.json', "{\"key\":\"value\"}")
        self.populate_resource('foo.csv', "one,two\n"
                                          "three,four"
                               )
        adapter = m.post('http://test.com')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue('Content-Type: text/csv' in adapter.last_request.text)
        self.assertTrue('Content-Type: application/json' in adapter.last_request.text)
        self.assertTrue("{\"key\":\"value\"}" in adapter.last_request.text)
        self.assertTrue("one,two\n"
                        "three,four" in adapter.last_request.text)

    @requests_mock.mock()
    def test_upload_template(self, m):
        self.populate_file('main.yaml', '''---
                                    variables:
                                        var: 'one'
                                    steps:
                                        - http: 
                                            post: 
                                                url: 'http://test.com'
                                                files:
                                                    file: 'foo.csv'
                                                    type: 'text/csv'
                                    ''')
        self.populate_resource('foo.csv', "{{var}},two\n"
                                          "three,four"
                               )

        adapter = m.post('http://test.com')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
        self.assertTrue('Content-Type: text/csv' in adapter.last_request.text)
        self.assertTrue("one,two\n"
                        "three,four" in adapter.last_request.text)

    @pytest.mark.skip(reason="Uses external service. Shouldn't be run automatically")
    def test_use_cookies(self):
        self.populate_file('main.yaml', '''---
                            steps:
                                - http: 
                                    get: 
                                        url: 'http://httpbin.org/cookies/set/sessioncookie/123456789'
                                - http:
                                    get:
                                        url: 'http://httpbin.org/cookies'
                                    register: {reply: '{{ OUTPUT }}'}
                                - check:
                                    equals: {the: '{{ reply.cookies.sessioncookie }}', is: '123456789'}
                            ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())

    @pytest.mark.skip(reason="Uses external service. Shouldn't be run automatically")
    def test_change_sessions(self):
        self.populate_file('main.yaml', '''---
                                    steps:
                                        - http: 
                                            get: 
                                                url: 'http://httpbin.org/cookies/set/sessioncookie/123456789'
                                                session: 'one'
                                        - http: 
                                            get: 
                                                url: 'http://httpbin.org/cookies/set/sessioncookie/987654321'
                                                session: 'two'
                                        - http:
                                            get:
                                                url: 'http://httpbin.org/cookies'
                                                session: 'one'
                                            register: {reply: '{{ OUTPUT }}'}
                                        - check:
                                            equals: {the: '{{ reply.cookies.sessioncookie }}', is: '123456789'}
                                        - http:
                                            get:
                                                url: 'http://httpbin.org/cookies'
                                                session: 'two'
                                            register: {reply: '{{ OUTPUT }}'}
                                        - check:
                                            equals: {the: '{{ reply.cookies.sessioncookie }}', is: '987654321'}
                                        - http: 
                                            get: 
                                                url: 'http://httpbin.org/cookies/set/sessioncookie/123456789'
                                                session: null
                                        - http:
                                            get:
                                                url: 'http://httpbin.org/cookies'
                                                session: null
                                            register: {reply: '{{ OUTPUT }}'}
                                        - check:   
                                            equals: {the: '{{ reply.cookies }}', is: '{}'}
                                        
                                    ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None)
        self.assertTrue(runner.run_tests())
