import collections
import itertools
import json

from catcher.steps.check import Operator
from catcher.steps.step import Step, update_variables
from catcher.utils.logger import debug
from catcher.utils.misc import fill_template_str, try_get_objects


class Loop(Step):
    """
    Repeat one or several actions till the condition is true or for each element of the collection. Is useful, when you
    need to wait for some process to start or for async execution to finish.

    :Input:

    :while: perform action while the condition is true

    - if: your condition. It can be in short format: `if: '{{ counter < 10 }}'` and
            long one: `if: {equals: {the: '{{ counter }}', is_not: 10000}}`. The clause
            format is the same as in [checks](checks.md)
    - do: the aciton to be performed. Can be a list of actions or single one.
    - max_cycle: the limit of reductions. *Optional* default is no limit.

    :foreach: iterate data structure

    - in: variable or static list. **ITEM** variable can be used to access each element of the data structure.
            Data structure can be list, dict or any other python data structure which supports iteration.
    - do: the action to be performed. Can be a list of actions or single one.

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

    def __init__(self, _get_action=None, _get_actions=None, **kwargs):
        super().__init__(**kwargs)
        self.type = Step.filter_predefined_keys(kwargs)  # while/foreach
        do = kwargs[self.type]['do']
        if len(do) == 1:  # just action
            if isinstance(do, list):  # list with single action
                do = do[0]
            [loop_action] = do.keys()
            self.do_action = [_get_action((loop_action, do[loop_action]))]
        else:
            self.do_action = list(itertools.chain.from_iterable([_get_actions(act) for act in do]))
        self.max_cycle = kwargs[self.type].get('max_cycle')
        if self.type == 'while':
            if_clause = kwargs['while']['if']
            if isinstance(if_clause, str):
                self.if_clause = {'equals': if_clause}
            else:
                self.if_clause = if_clause
        elif self.type == 'foreach':
            self.in_var = kwargs['foreach']['in']
        else:
            raise ValueError('Wrong configuration for step: ' + str(kwargs))

    @update_variables
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
            try:
                output = action.action(includes, output)
            except Exception as e:
                if action.ignore_errors:
                    debug('{} got {} but we ignore it'.format(fill_template_str(action.name, variables), e))
                    break
                raise e
        return output
