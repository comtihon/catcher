from abc import abstractmethod

from catcher.steps.step import Step
from catcher.utils.logger import debug
from catcher.utils.misc import get_all_subclasses_of, fill_template


class Operator(object):
    def __init__(self, body: dict, negative=False) -> None:
        self._subject = body
        self._negative = negative

    @property
    def negative(self) -> bool:
        return self._negative

    @negative.setter
    def negative(self, new_value: bool):
        self._negative = new_value

    @property
    def body(self) -> any:
        return self.__class__.__name__.lower()

    @property
    def subject(self) -> dict:
        return self._subject

    @abstractmethod
    def operation(self, variables: dict) -> bool:
        pass

    @staticmethod
    def find_operator(source: dict or str) -> 'Operator':
        if isinstance(source, str):
            operator_str = 'equals'
        else:
            [operator_str] = source.keys()
        operators = get_all_subclasses_of(Operator)
        named = dict([(o.__name__.lower(), o) for o in operators])
        if operator_str not in named:
            raise RuntimeError('No ' + operator_str + ' available')
        cls = named[operator_str]
        return cls(source)


class Equals(Operator):
    @staticmethod
    def to_long_form(source: any, value: any):
        return {'the': source, 'is': value}

    def determine_source(self, body: dict):
        if 'is' in body:
            return body['is']
        self.negative = True
        return body['is_not']

    def operation(self, variables: dict) -> bool:
        if isinstance(self.subject, str):
            subject = fill_template(self.subject, variables)
            source = True
        else:
            body = self.subject[self.body]
            if isinstance(body, str):
                body = Equals.to_long_form(body, True)
            subject = fill_template(body['the'], variables)
            source = fill_template(self.determine_source(body), variables)
        result = source == subject
        if self.negative:
            result = not result
        if not result:
            debug(str(source) + ' is not equal to ' + str(subject))
        return result


class Contains(Operator):
    @staticmethod
    def to_long_form(source: any, value: any):
        return {'the': source, 'in': value}

    def determine_source(self, body: dict):
        if 'in' in body:
            return body['in']
        self.negative = True
        return body['not_in']

    def operation(self, variables: dict):
        body = self.subject[self.body]
        source = fill_template(self.determine_source(body), variables)
        subject = fill_template(body['the'], variables)
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
            next_operation = Operator.find_operator(operator)
            if next_operation.operation(variables) == self.end:
                return self.end
        return True


class Or(And):
    @property
    def end(self):
        return True


class All(Operator):
    def operator(self, data):
        return all(data)

    def operation(self, variables) -> bool:
        body = self.subject[self.body]
        source = fill_template(body['of'], variables)
        if isinstance(source, list):
            elements = source
        elif isinstance(source, dict):
            elements = source.items()
        else:
            debug(str(source) + ' not iterable')
            return False
        results = []
        for element in elements:
            oper_body = dict([(k, v) for (k, v) in body.items() if k != 'of'])
            [next_operator] = oper_body.keys()
            if not isinstance(oper_body[next_operator], dict):  # terminator in short form
                if next_operator == 'equals':
                    oper_body[next_operator] = Equals.to_long_form('{{ ITEM }}', oper_body[next_operator])
                if next_operator == 'contains':
                    oper_body[next_operator] = Contains.to_long_form('{{ ITEM }}', oper_body[next_operator])
            next_operation = Operator.find_operator(oper_body)
            variables['ITEM'] = element
            results.append(next_operation.operation(variables))
        return self.operator(results)


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
            raise RuntimeError('operation ' + str(self.subject) + ' failed')
        return self.process_register(variables)
