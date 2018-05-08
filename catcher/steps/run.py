from catcher.steps.step import Step
from catcher.utils.logger import error
from catcher.utils.misc import merge_two_dicts, fill_template_str
from catcher.steps.stop import StopException


class Run(Step):
    def __init__(self, **keywords) -> None:
        super().__init__(keywords)
        self._variables = keywords.get('variables', {})
        self._ignore_errors = keywords.get('ignore_errors', False)
        self._include = keywords.get('include', None)
        self._tag = keywords.get('tag', None)
        if self.include is None:
            self._include = keywords['run']

    @property
    def include(self):
        return self._include

    @property
    def tag(self):
        return self._tag

    @property
    def ignore_errors(self) -> bool:
        return self._ignore_errors

    @property
    def variables(self) -> dict:
        return self._variables

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
        return self.process_register(variables)


def get_tag(include: str, tag: str or None) -> str or None:
    if tag is not None:
        return include, tag
    if '.' in include:
        splitted = include.split('.')
        return splitted[0], splitted[-1:][0]
    else:
        return include, None
