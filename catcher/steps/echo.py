import os
from os.path import join

from catcher.steps.step import Step, update_variables
from catcher.utils.file_utils import read_file
from catcher.utils.logger import info
from catcher.utils.misc import fill_template, fill_template_str


class Echo(Step):
    """
    :Input:

    :from: data source. Can be variable or constant string
    :from_file: file in resources.
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

    Read file content to a variable
    ::

        echo: {from_file: debug.output, to: '{{ user_email }}'}

    """

    def __init__(self, _path: str = None, _body=None, to=None, from_file=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source = _body if _body else kwargs.get('from')
        self.source_file = from_file
        self.dst = to
        self.path = _path
        if self.source is None and self.source_file is None:
            raise ValueError('Incorrect arguments for echo.')

    @update_variables
    def action(self, includes: dict, variables: dict) -> tuple:
        if self.source_file:  # read from file
            resources = variables['RESOURCES_DIR']
            out = fill_template_str(read_file(os.path.join(resources, self.source_file)), variables)
        else:
            out = fill_template(self.source, variables)
        if self.dst is None:
            info(out)
        else:
            dst = fill_template(self.dst, variables)
            with open(join(self.path, dst), 'w') as f:
                f.write(str(out))
        return variables, out
