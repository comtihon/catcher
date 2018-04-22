from catcher.steps.check import Operator

from catcher.steps.step import Step


class StopException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Stop(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        self._end_if = body['if']

    @property
    def end_if(self) -> dict:
        return self._end_if

    def action(self, includes: dict, variables: dict) -> dict:
        operator = Operator.find_operator(self.end_if)
        if operator.operation(variables):
            raise StopException(str(self.end_if) + ' fired')
        else:
            return self.process_register(variables)
