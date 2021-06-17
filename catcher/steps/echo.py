import os
from os.path import join

from catcher.steps.step import Step, update_variables
from catcher.utils.file_utils import read_file
from catcher.utils.logger import info
from catcher.utils.misc import fill_template, fill_template_str
from catcher.utils import file_utils, module_utils


class Echo(Step):
    """
    Print a string constant, variable or file to the console or file.

    :Input:

    :from: data source. Can be variable or constant string
    :from_file: file in resources.
    :to: output to file. *Optional* If not set - stdout will be used. **Not** resources-related

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
            out = self._read_file(variables)
        else:
            out = fill_template(self.source, variables)
        if self.dst is None:
            info(out)
        else:
            dst = fill_template(self.dst, variables)
            path = fill_template(self.path, variables)
            filename = join(path, dst)
            file_utils.ensure_dir(os.path.dirname(os.path.abspath(filename)))
            with open(filename, 'w') as f:
                f.write(str(out))
        return variables, out

    def _read_file(self, variables):
        resources = variables['RESOURCES_DIR']
        file = join(resources, fill_template_str(self.source_file, variables))
        if self.source_file.endswith('.py'):
            try:
                read = module_utils.load_external_actions(file)
                if read is None:
                    raise Exception("Can't parse file")
                external = [f for f in dir(read) if not f.startswith('__')]  # load not internal values as output
                return dict([(n, getattr(read, n)) for n in external])
            except Exception:  # if we can't parse python file - return it as string (old normal way)
                return fill_template_str(read_file(file), variables)
        else:
            return fill_template_str(read_file(file), variables)
