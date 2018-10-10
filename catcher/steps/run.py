from catcher.steps.step import Step, update_variables
from catcher.utils.logger import error
from catcher.utils.misc import merge_two_dicts, fill_template_str
from catcher.steps.stop import StopException


class Run(Step):
    """
    Run include on demand

    :Input:

    :include: include name
    :tag: include tag. *Optional* If specified - only steps with this tag will be run. Can also be set up via dot notation: `include: test.tag`.
    :variables: Variables to override. *Optional*

    :Examples:

    Use short form to run `sign_up`
    ::

        include:
            file: register_user.yaml
            as: sign_up
        steps:
            # .... some steps
            - run: sign_up
            # .... some steps

    Run `sign_up` with username overridden
    ::

        include:
            file: register_user.yaml
            as: sign_up
        steps:
            # .... some steps
            - run:
                include: sign_up
                variables:
                    username: test
            # .... some steps

    Include `sign_up` and run all steps with tag `register` from it. Use dot notation.
    ::

        include:
            file: register_and_login.yaml
            as: sign_up
        steps:
            - run:
                include: sign_up.register
    """

    def __init__(self, ignore_errors=False, _body=None, run=None, include=None, tag=None, variables=None, **keywords):
        super().__init__(keywords)
        self.variables = {} if variables is None else variables
        self.ignore_errors = ignore_errors
        self.include = include
        self.tag = tag
        if self.include is None:
            if run and isinstance(run, str):
                self.include = run
            else:
                self.include = _body

    @update_variables
    def action(self, includes: dict, variables: dict) -> dict:
        filled_vars = dict([(k, fill_template_str(v, variables)) for (k, v) in self.variables.items()])
        out = fill_template_str(self.include, variables)
        test, tag = get_tag(out, self.tag)
        if test not in includes:
            error('No include registered for name ' + test)
            raise Exception('No include registered for name ' + test)
        include = includes[test]
        variables = merge_two_dicts(include.variables, merge_two_dicts(variables, filled_vars))
        include.variables = variables
        try:
            variables = include.run(tag=tag, raise_stop=True)
        except StopException as e:
            raise e
        except Exception as e:
            if not self.ignore_errors:
                raise Exception('Step run ' + test + ' failed: ' + str(e))
        return variables


def get_tag(include: str, tag: str or None) -> str or None:
    if tag is not None:
        return include, tag
    if '.' in include:
        splitted = include.split('.')
        return splitted[0], splitted[-1:][0]
    else:
        return include, None
