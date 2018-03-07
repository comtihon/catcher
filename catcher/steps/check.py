from abc import abstractmethod

from catcher.steps.step import Step
from catcher.utils.logger import debug
from catcher.utils.misc import merge_two_dicts, get_all_subclasses_of, fill_template

NEGATIVE_RULES = ['equals', 'contains']


class Operator(object):
    def __init__(self, body: dict, negative=False) -> None:
        self._subject = body
        self._negative = negative

    @property
    def negative(self) -> bool:
        return self._negative

    @property
    def source(self) -> str:
        return self.subject['the']

    @property
    def body(self) -> any:
        classname = self.__class__.__name__.lower()
        if self.negative and classname in NEGATIVE_RULES:
            return 'not_' + classname
        return classname

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
        operator_str, negative = Operator.find_negate(operator_str)
        operators = get_all_subclasses_of(Operator)
        named = dict([(o.__name__.lower(), o) for o in operators])
        if operator_str not in named:
            raise RuntimeError('No ' + operator_str + ' available')
        cls = named[operator_str]
        return cls(source, negative)

    @staticmethod
    def find_negate(operator: str) -> (str, bool):
        if operator.startswith('not_'):
            [splitted] = [f for f in operator.split('not_') if f is not '']
            if splitted in NEGATIVE_RULES:
                return splitted, True
        return operator, False


class Equals(Operator):
    def operation(self, variables: dict) -> bool:
        source = fill_template(self.source, variables)
        subject = fill_template(self.subject[self.body], variables)
        result = source == subject
        if self.negative:
            result = not result
        if not result:
            debug(str(source) + ' is not equal to ' + str(subject))
        return result


class Contains(Operator):
    def operation(self, variables: dict):
        source = fill_template(self.source, variables)
        subject = fill_template(self.subject[self.body], variables)
        result = subject in source
        if self.negative:
            result = not result
        if not result:
            debug(str(subject) + ' is not in ' + str(source))
        return result


class And(Operator):
    @property
    def end(self) -> bool:
        return False

    def operation(self, variables) -> bool:
        operators = self.subject[self.body]  # or or and
        for operator in operators:
            body = self.get_next_operator(operator, variables)
            next_operation = Operator.find_operator(body)
            if next_operation.operation(variables) == self.end:
                return self.end
        return True

    def get_next_operator(self, operator: dict, variables: dict) -> dict:
        [body] = list(operator.values())
        if 'the' not in body:
            source = fill_template(self.source, variables)
            body = merge_two_dicts(operator, {'the': source})
        [key] = [k for k in operator.keys() if k != 'the']
        splitted = key.split('not_')
        if len(splitted) > 1 and splitted[1] in body:
            body[key] = body[splitted[1]]
            body.pop(splitted[1])
        return body


class Or(And):
    @property
    def end(self):
        return True


class All(Operator):
    def operator(self, data):
        return all(data)

    def operation(self, variables) -> bool:
        source = fill_template(self.source, variables)
        if isinstance(source, list):
            results = []
            for element in source:
                option = self.body  # all or any
                subject = self.subject[option]
                if 'the' not in self.subject[option]:
                    subject = merge_two_dicts(self.subject[option], {'the': element})
                next_operation = Operator.find_operator(subject)
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
