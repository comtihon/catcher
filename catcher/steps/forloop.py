import collections
import json

from catcher.steps.check import Operator
from catcher.steps.step import Step
from catcher.utils.misc import fill_template_str, try_get_objects


class ForLoop(Step):
    """
    :Input:

    :while: perform action while the condition is true

    - if: your condition. It can be in short format: `if: '{{ counter < 10 }}'` and
long one: `if: {equals: {the: '{{ counter }}', is_not: 10000}}`. The clause
format is the same as in [checks](checks.md)
    - do: the aciton to be performed. Can be a list of actions or single one.
    - max_cycle: the limit of reductions. *Optional* default is no limit.

    :foreach: iterate data structure

    - in: variable or static list. `ITEM` variable can be used to access each element of the data structure.
    Data structure can be list, dict or any other python data structure which supports iteration.
    - do: the aciton to be performed. Can be a list of actions or single one.

    :Examples:

    Perform a single echo wile counter is less than 10
    ::
        loop:
            while:
                if: '{{ counter < 10 }}'
                do:
                    echo: {from: '{{ counter + 1 }}', register: {counter: '{{ OUTPUT }}'}}
                max_cycle: 100000

    Perform to actions: consume message from kafka and send token via POST http. Do it until server
    returns passed true in http response.
    ::
        loop:
            while:
                if:
                    equals: {the: '{{ passed }}', is_not: True}
                do:
                    - kafka:
                          consume:
                              server: '127.0.0.1:9092'
                              group_id: 'test'
                              topic: 'test_consume_with_timestamp'
                              timeout: {seconds: 5}
                              where:
                                  equals: '{{ MESSAGE.timestamp > 1000 }}'
                          register: {token: '{{ OUTPUT.data.token }}'}
                    - http:
                        post:
                          headers: {Content-Type: 'application/json'}
                          url: 'http://test.com/check_my_token'
                          body: {'token': '{{ token }}'}
                        register: {passed: '{{ OUTPUT.passed }}'}

    Iterate over `iterator` variable, produce each element to kafka as json and debug it to file.
    ::
        loop:
            foreach:
                in: '{{ iterator }}'
                do:
                    - kafka:
                          produce:
                              server: '127.0.0.1:9092'
                              topic: 'test_produce_json'
                              data: '{{ ITEM|tojson }}'
                    - echo: {from: '{{ ITEM }}', to: '{{ ITEM["filename"] }}.output'}

    """
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        self._type = Step.filter_predefined_keys(body)  # while/foreach
        self._max_cycle = body[self._type].get('max_cycle')
        self._do = body[self._type]['do']
        if self._type == 'while':
            if_clause = body['while']['if']
            if isinstance(if_clause, str):
                self._if = {'equals': if_clause}
            else:
                self._if = if_clause
        elif self._type == 'foreach':
            self._in = body['foreach']['in']
        else:
            raise ValueError('Wrong configuration for step: ' + str(body))
        self._do_action = None

    @property
    def type(self) -> str:
        return self._type

    @property
    def max_cycle(self) -> int or None:
        return self._max_cycle

    @max_cycle.setter
    def max_cycle(self, new_value):
        self._max_cycle = new_value

    @property
    def do(self) -> dict or list:
        return self._do

    @property
    def do_action(self) -> [Step]:
        return self._do_action

    @do_action.setter
    def do_action(self, action: list):
        self._do_action = action

    @property
    def if_clause(self) -> dict or None:
        return self._if

    @property
    def in_var(self) -> str or None:
        return self._in

    def action(self, includes: dict, variables: dict) -> dict:
        output = variables
        if self.type == 'while':
            operator = Operator.find_operator(self.if_clause)
            while operator.operation(output):
                output = self.__run_actions(includes, output)
                if self.max_cycle is not None:
                    if self.max_cycle == 0:
                        break
                    self.max_cycle = self.max_cycle - 1
            return output
        elif self.type == 'foreach':
            loop_var = try_get_objects(fill_template_str(json.dumps(self.in_var), variables))
            if not isinstance(loop_var, collections.Iterable):
                raise ValueError(str(loop_var) + ' is not iterable')
            for entry in loop_var:
                output['ITEM'] = entry
                output = self.__run_actions(includes, output)
        return output

    def __run_actions(self, includes, variables: dict) -> dict:
        output = variables
        for action in self.do_action:
            output = action.action(includes, output)
        return output
