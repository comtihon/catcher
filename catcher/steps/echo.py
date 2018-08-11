from os.path import join

from catcher.steps.step import Step, update_variables
from catcher.utils.logger import info
from catcher.utils.misc import fill_template


class Echo(Step):
    """
    :Input:

    :from: data source. Can be variable or constant string
    :to: output to file. *Optional* If not set - stdout will be used.

    Has short from which just prints variable to stdout.

    :Examples:

    Use short form to print variable to stdout
    ::

        echo: '{{ var }}'

    Print constant + variable to file
    ::

        echo: {from: 'constant and {{ var }}', to: debug.output}

    Use echo to register new variable
    ::

        echo: {from: '{{ RANDOM_STR }}@test.com', register: {user_email: '{{ OUTPUT }}'}}

    """

    def __init__(self, body: dict, path: str = None) -> None:
        super().__init__(body)
        if isinstance(body, dict):
            self.source = body['from']
            self.dst = body.get('to', None)
        elif isinstance(body, str):
            self.source = body
            self.dst = None
        else:
            raise ValueError('Incorrect arguments for echo.')
        self.path = path

    @classmethod
    def construct_step(cls, body, *params, **kwargs):
        return cls(body, *params)

    @update_variables
    def action(self, includes: dict, variables: dict) -> tuple:
        out = fill_template(self.source, variables)
        if self.dst is None:
            info(out)
        else:
            dst = fill_template(self.dst, variables)
            with open(join(self.path, dst), 'w') as f:
                f.write(str(out))
        return variables, out
