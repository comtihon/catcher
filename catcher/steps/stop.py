from catcher.steps.check import Operator

from catcher.steps.step import Step, update_variables


class StopException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Stop(Step):
    """
    Stop a test without error

    :Input:

    :if: condition

    :Examples:

    Stop execution if migration was applied.
    ::

        steps:
            - postgres:
                request:
                    conf: '{{ migrations_postgres }}'
                    query: "select count(*) from migration where hash = '{{ TEST_NAME }}';"
                register: {result: '{{ OUTPUT }}'}
                tag: check
                name: 'check_migration_{{ TEST_NAME }}'
            - stop:
                if:
                    equals: {the: '{{ result }}', is: 1}
            - postgres:
                request:
                    conf: '{{ migrations_postgres }}'
                    query: "insert into migration(id, hash) values(1, '{{ TEST_NAME }}');"
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.end_if = kwargs['if']

    @update_variables
    def action(self, includes: dict, variables: dict) -> dict:
        operator = Operator.find_operator(self.end_if)
        if operator.operation(variables):
            raise StopException(str(self.end_if) + ' fired')
        else:
            return variables
