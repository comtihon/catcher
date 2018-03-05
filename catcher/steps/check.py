from abc import abstractmethod

from jinja2 import Template

from catcher.steps.step import Step


class Operator(object):
    def __init__(self, source, next_operation=None) -> None:
        self._source = source
        self._next_operation = next_operation

    @property
    def next_operation(self):
        return self._next_operation

    @property
    def source(self):
        return self._source

    @abstractmethod
    def operation(self, input_data) -> bool:
        pass

    @staticmethod
    def find_operator(body: dict) -> 'Operator':
        keys = list(body.keys())
        keys.remove('the')
        [operator_str] = keys
        operators = Operator.__subclasses__()
        named = dict([(o.__name__.lower(), o) for o in operators])
        if operator_str not in named:
            raise RuntimeError('No ' + operator_str + ' available')
        cls = named[operator_str]
        #  TODO fix getting keys, source and next_operation
        return cls.__new__(keys[operator_str])


class Equals(Operator):  # TODO add negate option
    def operation(self, input_data) -> bool:
        return self.source == input_data


class Contains(Operator):  # TODO add negate option
    def operation(self, input_data):
        return self.source in input_data


class And(Operator):
    def operation(self, input_data) -> bool:
        pass


class Or(Operator):
    def operation(self, input_data) -> bool:
        pass


class All(Operator):
    def __init__(self, source, next_operation: Operator) -> None:
        super().__init__(source, next_operation)

    def operation(self, input_data) -> bool:
        if isinstance(input_data, list):
            return all(self.operation(data) for data in input_data)
        elif isinstance(input_data, dict):
            return all(self.operation(v) for (k, v) in input_data)
        else:
            return False


class Any(Operator):
    def __init__(self, source, next_operation: Operator) -> None:
        super().__init__(source, next_operation)

    def operation(self, input_data) -> bool:
        if isinstance(input_data, list):
            return any(self.operation(data) for data in input_data)
        elif isinstance(input_data, dict):
            return any(self.operation(v) for (k, v) in input_data)
        else:
            return False


class Check(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        self._subject = body

    @property
    def source(self) -> str:
        return self._subject['the']

    @property
    def subject(self) -> dict:
        return self._subject

    def action(self, includes: dict, variables: dict) -> dict:
        template = Template(self.source)
        source = template.render(variables)
        operator = Operator.find_operator(self.subject)
        if not operator.operation(source):
            raise RuntimeError('operation failed')
        return self.process_register(variables)
