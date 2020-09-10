import json
import os
import re
from typing import Union, Optional

import requests

from catcher.steps.step import Step, update_variables
from catcher.utils.logger import debug, warning
from catcher.utils.misc import fill_template, fill_template_str
from catcher.utils import file_utils


class Http(Step):
    """
    Perform an http request: from just getting the information from the server to pushing a file to it.

    :Input:

    :<method>: http method. Most frequent are get/post/put/delete.
     See `docs <https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html>`_ for details

    - headers: Dictionary with custom headers. *Optional*
    - url: url to call
    - response_code: Code to await. Use 'x' for a wildcard or '-' to set a range between 2 codes.
                     *Optional* default is 200.
    - body: body to send. *Optional*.
    - body_from_file: File can be used as data source. *Optional*.
    - files: send file from resources (only for methods which support it). *Optional*
    - verify: Verify SSL Certificate in case of https. *Optional*. Default is true.
    - should_fail: true, if this request should fail, f.e. to test connection refused. Will fail the test if no errors.
    - session: http session name. Cookies are saved between sessions. *Optional*. Default session is 'default'.
               If set to null - there would be no session.
    - fix_cookies: if true will make cookies secure if you use https and not secure if you don't. *Optional*.
                   Default is true. Is useful when you don't have tls for your test env, but can't change infra.
    - timeout: number of seconds to wait for response. *Optional*. Default is no timeout (wait forever)

    :files: is a single file or list of files, where <file_param> is a name of request param.
            If you don't specify headers 'multipart/form-data' will be set automatically.

    - <file_param>: path to the file
    - type: file mime type

    :cookies: All requests are run in the session, sharing cookies got from previous requests. If you wish to
              start new empty session use `session`. If you don't want a session to be saved use `session: null`

    :Examples:

    Put data to server and await 200-299 code
    ::

        http:
          put:
            url: 'http://test.com?user_id={{ user_id }}'
            body: {'foo': bar}
            response_code: 2XX

    Put data to server and await 201-3XX code
    ::

        http:
          put:
            url: 'http://test.com?user_id={{ user_id }}'
            body: {'foo': bar}
            response_code: 201-3xx

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

    Manual set of json body. tojson will convert 'var' to json string
    ::

        http:
          post:
            url: 'http://test.com?user_id={{ user_id }}'
            body: '{{ var |tojson }}'

    Set json by providing json headers and passing python object to body
    ::

        http:
          post:
            url: 'http://test.com?user_id={{ user_id }}'
            headers: {Content-Type: 'application/json'}
            body: '{{ var  }}'

    Send file with a post request
    ::

        http:
          post:
            url: 'http://example.com/upload'
            files:
                file: 'subdir/my_file_in_resources.csv'
                type: 'text/csv'

    Send multiple files with a single post request
    ::

        http:
          post:
            url: 'http://example.com/upload'
            files:
                - my_csv_file: 'one.csv'
                  type: 'text/csv'
                - my_json_file: 'two.json'
                  type: 'application/json'

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

    Test correct and incorrect login (clear cookies):
    ::

        steps:
            - http:
                post:
                    url: 'http://test.com/login.php?user_id={{ user_id }}'
                    body: {'pwd': secret}
                    response_code: 2XX
                    session: 'user1'
                name: "Do a login"
            - http:
                get:
                    url: 'http://test.com/protected_path'
                    response_code: 2XX
                    session: 'user1'
                name: "Logged-in user can access protected_path"
            - http:
                get:
                    url: 'http://test.com/protected_path'
                    response_code: 401
                    session: 'user2'
                name: "protected_path can't be accessed without login"
    """
    sessions = {}

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        method = Step.filter_predefined_keys(kwargs)  # get/post/put...
        self.method = method.lower()
        conf = kwargs[method]
        self.url = conf['url']
        self.headers = conf.get('headers', {})
        self.verify = conf.get('verify', True)
        self._should_fail = conf.get('should_fail', False)
        if not self.verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.code = conf.get('response_code', 200)
        self.body = conf.get('body')
        self.file = conf.get('body_from_file')
        self.files = conf.get('files')
        self.session = conf.get('session', 'default')
        self.fix_cookies = conf.get('fix_cookies', True)
        self.timeout = conf.get('timeout')

    @update_variables
    def action(self, includes: dict, variables: dict) -> Union[tuple, dict]:
        url = fill_template(self.url, variables)
        session = Http.sessions.get(self.session, requests.Session())
        r = None
        try:
            r = session.request(self.method, url, **self._form_request(url, variables))
            if self._should_fail:  # fail expected
                raise RuntimeError('Request expected to fail, but it doesn\'t')
        except requests.exceptions.ConnectionError as e:
            debug(str(e))
            if self._should_fail:  # fail expected
                return variables
        self.__fix_cookies(url, session)
        if self.session is not None:  # save session if name is specified
            Http.sessions[self.session] = session
        if r is None:
            raise Exception('No response received')
        debug(r.text)
        try:
            response = r.json()
        except ValueError:
            response = r.text
        if self.__check_code(r.status_code, self.code):
            raise RuntimeError('Code mismatch: ' + str(r.status_code) + ' vs ' + str(self.code))
        return variables, response

    def _form_request(self, url, variables: dict) -> dict:
        headers = dict([(fill_template_str(k, variables), fill_template_str(v, variables))
                        for k, v in self.headers.items()])
        rq = dict(verify=self.verify, headers=headers, files=self.__form_files(variables))
        isjson, body = self.__form_body(variables)
        debug('http ' + str(self.method) + ' ' + str(url) + ', ' + str(headers) + ', ' + str(body))
        content_type = self.__get_content_type(headers)
        if isjson or isinstance(body, dict):  # contains tojson or dict supplied
            if isinstance(body, dict) and content_type == 'application/json':
                # json body formed manually via python dict
                rq['json'] = body
            else:  # json string or form-data dict
                rq['data'] = body
        else:  # raw body (or body is None)
            rq['data'] = body
        rq['timeout'] = self.timeout
        return rq

    @staticmethod
    def __get_content_type(headers):
        content_type = headers.get('Content-Type')
        if content_type is None:
            content_type = headers.get('content-type')
        return content_type

    def __form_body(self, variables) -> tuple:
        if self.method == 'get':
            return False, None
        body = self.body
        if body is None and self.file is not None:
            resources = variables['RESOURCES_DIR']
            body = file_utils.read_file(fill_template_str(os.path.join(resources, self.file), variables))
        if isinstance(body, dict) or isinstance(body, list):  # dump body to json to be able fill templates in
            body = json.dumps(body)
        if body is None:
            return False, None
        isjson = 'tojson' in body
        return isjson, fill_template(body, variables, isjson=isjson)

    def __form_files(self, variables) -> Optional[list]:
        if self.files is not None:
            if isinstance(self.files, dict):
                return [self.__prepare_file(self.files, variables)]
            elif isinstance(self.files, list):
                return [self.__prepare_file(f, variables) for f in self.files]
            else:
                warning('Don\'t know how to prepare ' + type(self.files))
        return None

    def __fix_cookies(self, url: str, session):
        """
        If url was https and cookies received are not secure - make them secure.
        If url was http and cookies received are secure - make them not secure
        """
        if self.fix_cookies:
            secure = url.startswith('https')
            for site, cookies in session.cookies._cookies.items():
                for path, cookie_list in cookies.items():
                    for name, cookie in cookie_list.items():
                        cookie.secure = secure

    @staticmethod
    def __check_code(got: int, expected):
        expected_str = str(expected).lower()
        if '-' in str(expected_str):  # range
            [e_from, e_to] = expected_str.split('-')
            return not (int(e_from.replace('x', '0')) <= got <= int(e_to.replace('x', '9')))
        if 'x' in expected_str:  # regexp
            expected_str = expected_str.replace('x', '.')
        p = re.compile(expected_str)
        return p.match(str(got)) is None

    @staticmethod
    def __prepare_file(file: dict, variables: dict):
        resources = variables['RESOURCES_DIR']
        [file_key] = [k for k in file.keys() if k != 'type']
        filepath = file[file_key]
        file_type = file.get('type', 'text/plain')
        filename = file_utils.get_filename(filepath)
        file = fill_template_str(file_utils.read_file(os.path.join(resources, filepath)), variables)
        return file_key, (filename, file, file_type)
