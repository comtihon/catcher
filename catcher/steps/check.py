from abc import abstractmethod

from catcher.steps.step import Step, update_variables, SERVICE_KEYS
from catcher.utils.logger import debug
from catcher.utils.misc import fill_template
from catcher.utils.module_utils import get_all_subclasses_of


class Operator(object):
    def __init__(self, body: dict, negative=False) -> None:
        self.subject = body
        self.negative = negative

    @property
    def body(self) -> any:
        return self.__class__.__name__.lower()

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
    """
    Fail if elements are not equal

    :Input:
    :the: value
    :is: variable to compare
    :is_not: inverted `is`. Only one can be used at a time.

    :Examples:

    Check 'bar' equals variable 'foo'
    ::

        check: {equals: {the: 'bar', is: '{{ foo }}'}}

    Check list's third element is not greater than 2.
    ::

        check: {equals: {the: '{{ list[2] > 2 }}', is_not: true}}

    """

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

    def determine_source(self, body: dict):
        if 'is' in body:
            return body['is']
        self.negative = True
        return body['is_not']

    @staticmethod
    def to_long_form(source: any, value: any):
        return {'the': source, 'is': value}


class Contains(Operator):
    """
    Fail if list of dictionary doesn't contain the value

    :Input:
    :the: value to contain
    :in: variable to check
    :not_in: inverted `in`. Only one can be used at a time.

    :Examples:

    Check 'a' not in variable 'list'
    ::

        check:
            contains: {the: 'a', not_in: '{{ list }}'}

    Check variable 'dict' has key `a`.
    ::

        check:
            contains: {the: 'a', in: '{{ dict }}'}

    """

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

    def determine_source(self, body: dict):
        if 'in' in body:
            return body['in']
        self.negative = True
        return body['not_in']

    @staticmethod
    def to_long_form(source: any, value: any):
        return {'the': source, 'in': value}


class And(Operator):
    """
    Fail if any of the conditions fails.

    :Input: The list of other checks.

    :Examples:

    This is the same as `1 in list and list[1] != 'b' and list[2] > 2`
    ::

        check:
            and:
                - contains: {the: 1, in: '{{ list }}'}
                - equals: {the: '{{ list[1] }}', is_not: 'b'}
                - equals: {the: '{{ list[2] > 2 }}', is_not: true}

    """

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
    """
    Fail if all conditions fail.

    :Input: The list of other checks.

    :Examples:

    This is the same as `1 in list or list[1] != 'b' or list[2] > 2`
    ::

        check:
            or:
                - contains: {the: 1, in: '{{ list }}'}
                - equals: {the: '{{ list[1] }}', is_not: 'b'}
                - equals: {the: '{{ list[2] > 2 }}', is_not: true}

    """

    @property
    def end(self):
        return True


class All(Operator):
    """
    Fail if any check on the iterable fail.

    :Input:
    :of: The source to check. Can be list or dictionary.
    :<check>: Check to perform on each element of the iterable.

    :Examples:

    Pass if all elements of `var` has `k` == `a`
    ::

        check:
            all:
                of: '{{ var }}'
                equals: {the: '{{ ITEM.k }}', is: 'a'}

    """

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
    """
    Fail if all checks on the iterable fail.

    :Input:
    :of: The source to check. Can be list or dictionary.
    :<check>: Check to perform on each element of the iterable.

    :Examples:

    Fail if `var` doesn't contain element with `k` == `a`
    ::

        check:
            any:
                of: '{{ var }}'
                equals: {the: '{{ ITEM.k }}', is: 'a'}

    """

    def operator(self, data):
        return any(data)


class Check(Step):
    """
    Run check and fail if it was not successful.

    There are two types of checks: terminators and nodes. Terminators like `equals` or `contains`
    just perform checks while nodes contain like `all`, `any`, `or` and others contain other checks.

    Check has a short form
    ::

        check: '{{ variable }}'

    which equals
    ::

        check:
            equals: {the: '{{ variable }}', is: true}

    """

    def __init__(self, _body=None, **kwargs: dict) -> None:
        super().__init__(**kwargs)
        if _body:
            self.subject = _body
        else:
            [subject] = [{k: v} for k, v in kwargs.items() if k not in SERVICE_KEYS and not k.startswith('_')]
            self.subject = subject

    @update_variables
    def action(self, includes: dict, variables: dict) -> dict:
        operator = Operator.find_operator(self.subject)
        if not operator.operation(variables):
            raise RuntimeError('operation ' + str(self.subject) + ' failed')
        return variables
