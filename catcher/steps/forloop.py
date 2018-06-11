import collections
import json

from catcher.steps.check import Operator
from catcher.steps.step import Step
from catcher.utils.misc import fill_template_str, try_get_objects


class ForLoop(Step):

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
