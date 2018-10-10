import json

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
        if not self.verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.code = response_code
        if self.method != 'get':
            self.body = conf.get('body', None)
            if self.body is None:
                self.file = conf['body_from_file']

    @update_variables
    def action(self, includes: dict, variables: dict) -> tuple:
        url = fill_template(self.url, variables)
        headers = dict(
            [(fill_template_str(k, variables), fill_template_str(v, variables)) for k, v in self.headers.items()])
        body = self.__form_body(variables)
        debug('http ' + str(self.method) + ' ' + str(url) + ', ' + str(headers) + ', ' + str(body))
        if body is None:
            r = request(self.method, url, headers=headers, verify=self.verify)
        elif isinstance(body, dict):
            r = request(self.method, url, headers=headers, json=body, verify=self.verify)
        else:
            r = request(self.method, url, headers=headers, data=body, verify=self.verify)
        debug(r.text)
        if r.status_code != self.code:
            raise RuntimeError('Code mismatch: ' + str(r.status_code) + ' vs ' + str(self.code))
        try:
            response = r.json()
        except ValueError:
            response = r.text
        return variables, response

    def __form_body(self, variables) -> str or dict:
        if self.method == 'get':
            return None
        body = self.body
        if body is None:
            body = read_file(fill_template_str(self.file, variables))
        if isinstance(body, dict):  # dump body to json to be able fill templates in
            body = json.dumps(body)
        return fill_template(body, variables)
