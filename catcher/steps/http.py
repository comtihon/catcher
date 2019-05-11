import json
from typing import Union

import requests
from requests import request

from catcher.steps.step import Step, update_variables
from catcher.utils.file_utils import read_file
from catcher.utils.logger import debug
from catcher.utils.misc import fill_template, fill_template_str


class Http(Step):
    """
    :Input:

    :<method>: http method. See https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html for details

    - headers: Dictionary with custom headers. *Optional*
    - url: url to call
    - response_code: Code to await. *Optional* default is 200.
    - body: body to send (only for methods which support it).
    - body_from_file: File can be used as data source. *Optional* Either `body` or `body_from_file` should present.
    - verify: Verify SSL Certificate in case of https. *Optional*. Default is true.
    - should_fail: true, if this request should fail, f.e. to test connection refused. Will fail the test if no errors.

    :Examples:

    Post data to server with custom header
    ::

        http:
          post:
            headers: {Content-Type: 'application/json', Authorization: '{{ token }}'}
            url: 'http://test.com?user_id={{ user_id }}'
            body: {'foo': bar}

    Post file to remote server
    ::

        http:
          post:
            url: 'http://test.com'
            body_from_file: "data/answers.json"

    SSL without verification
    ::

        http:
          post:
            url: 'https://my_server.de'
            body: {'user':'test'}
            verify: false

    Json body from a variable:
    ::

        http:
          post:
            url: 'http://test.com?user_id={{ user_id }}'
            body: '{{ var |tojson }}'


    Test disconnected service:
    ::

        steps:
        - docker:
            disconnect:
                hash: '{{ my_container }}'
        - http:
            get:
                url: '{{ my_container_url }}'
                should_fail: true
    """

    def __init__(self, response_code=200, **kwargs) -> None:
        super().__init__(**kwargs)
        method = Step.filter_predefined_keys(kwargs)  # get/post/put...
        self.method = method.lower()
        conf = kwargs[method]
        self.url = conf['url']
        self.headers = conf.get('headers', {})
        self.body = None
        self.verify = conf.get('verify', True)
        self._should_fail = conf.get('should_fail', False)
        if not self.verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.code = response_code
        if self.method != 'get':
            self.body = conf.get('body', None)
            if self.body is None:
                self.file = conf['body_from_file']

    @update_variables
    def action(self, includes: dict, variables: dict) -> Union[tuple, dict]:
        url = fill_template(self.url, variables)
        r = None
        try:
            r = request(self.method, url, **self._form_request(url, variables))
            if self._should_fail:  # fail expected
                raise RuntimeError('Request expected to fail, but it doesn\'t')
        except requests.exceptions.ConnectionError as e:
            debug(str(e))
            if self._should_fail:  # fail expected
                return variables
        debug(r.text)
        if r.status_code != self.code:
            raise RuntimeError('Code mismatch: ' + str(r.status_code) + ' vs ' + str(self.code))
        try:
            response = r.json()
        except ValueError:
            response = r.text
        return variables, response

    def _form_request(self, url, variables: dict) -> dict:
        headers = dict([(fill_template_str(k, variables), fill_template_str(v, variables))
                        for k, v in self.headers.items()])
        rq = dict(verify=self.verify, headers=headers)
        isjson, body = self.__form_body(variables)
        debug('http ' + str(self.method) + ' ' + str(url) + ', ' + str(headers) + ', ' + str(body))
        if isjson or isinstance(body, dict):  # contains tojson or dict supplied
            if 'content-type' not in headers and 'Content-Type' not in headers:  # add json content type if missing
                headers['content-type'] = 'application/json'
            if isinstance(body, dict):  # json body formed manually via python dict
                rq['json'] = body
            else:  # string, already in json
                rq['data'] = body
        else:  # raw body (or body is None)
            rq['data'] = body
        return rq

    def __form_body(self, variables) -> str or dict:
        if self.method == 'get':
            return False, None
        body = self.body
        if body is None:
            body = read_file(fill_template_str(self.file, variables))
        if isinstance(body, dict):  # dump body to json to be able fill templates in
            body = json.dumps(body)
        isjson = 'tojson' in body
        return isjson, fill_template(body, variables, isjson=isjson)
