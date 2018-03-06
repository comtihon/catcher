import ast
from abc import abstractmethod

from jinja2 import Template

from catcher.steps.step import Step
from catcher.utils.logger import debug
from catcher.utils.misc import merge_two_dicts, get_all_subclasses_of


class Operator(object):
    def __init__(self, body: dict) -> None:
        self._subject = body

    @property
    def source(self) -> str:
        return self.subject['the']

    @property
    def subject(self) -> dict:
        return self._subject

    @abstractmethod
    def operation(self, variables: dict) -> bool:
        pass

    @staticmethod
    def find_operator(source: dict) -> 'Operator':
        keys = list(source.keys())
        if 'the' in keys:
            keys.remove('the')
        [operator_str] = keys
        operators = get_all_subclasses_of(Operator)
        named = dict([(o.__name__.lower(), o) for o in operators])
        if operator_str not in named:
            raise RuntimeError('No ' + operator_str + ' available')
        cls = named[operator_str]
        return cls(source)


class Equals(Operator):  # TODO add negate option
    def operation(self, variables: dict) -> bool:
        source = self.source
        if isinstance(source, str):
            source = Template(self.source).render(variables)
        subject = self.subject['equals']
        if isinstance(subject, str):
            subject = Template(subject).render(variables)
        result = source == subject
        if not result:
            debug(source + ' is not equal to ' + subject)
        return result


class Contains(Operator):  # TODO add negate option
    def operation(self, input_data):
        # TODO templating
        return self.source in input_data


class And(Operator):
    def operation(self, input_data) -> bool:
        pass


class Or(Operator):
    def operation(self, input_data) -> bool:
        pass


class All(Operator):
    def operator(self, data):
        return all(data)

    def operation(self, variables) -> bool:
        source = self.source
        if isinstance(source, str):
            source = Template(source).render(variables)
            source = ast.literal_eval(source)
        if isinstance(source, list):
            results = []
            for element in source:
                subject = {'the': element}
                option = self.__class__.__name__.lower()  # all or any
                next_operation = Operator.find_operator(merge_two_dicts(self.subject[option], subject))
                results.append(next_operation.operation(variables))
            return self.operator(results)
        else:
            return False


class Any(All):
    def operator(self, data):
        return any(data)


class Check(Step):
    def __init__(self, body: dict) -> None:
        super().__init__(body)
        self._subject = body

    @property
    def subject(self) -> dict:
        return self._subject

    def action(self, includes: dict, variables: dict) -> dict:
        operator = Operator.find_operator(self.subject)
        if not operator.operation(variables):
            raise RuntimeError('operation failed')
        return self.process_register(variables)
