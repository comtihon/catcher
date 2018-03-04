from jinja2 import Template

from catcher.steps.step import Step
from catcher.utils.logger import error
from catcher.utils.misc import merge_two_dicts


class Run(Step):
    def __init__(self, **keywords) -> None:
        super().__init__(keywords)
        self._variables = keywords.get('variables', {})
        self._ignore_errors = keywords.get('ignore_errors', False)
        self._include = keywords.get('include', None)
        if self.include is None:
            self._include = keywords['run']

    @property
    def include(self):
        return self._include

    @property
    def ignore_errors(self) -> bool:
        return self._ignore_errors

    @property
    def variables(self) -> dict:
        return self._variables

    def action(self, includes: dict, variables: dict) -> dict:
        template = Template(self.include)
        out = template.render(variables)
        test, tag = get_tag(out)
        if test not in includes:
            error('No include registered for name ' + test)
            raise Exception('No include registered for name ' + test)
        include = includes[test]
        variables = merge_two_dicts(include.variables, self.variables)
        include.variables = variables
        result, variables = include.run(tag=tag)
        if result or self.ignore_errors:
            return self.process_register(variables)
        else:
            error('Step run ' + test + ' failed')
            raise Exception('Step run ' + test + ' failed')


def get_tag(include: str) -> str or None:
    if '.' in include:
        splitted = include.split('.')
        return splitted[0], splitted[-1:][0]
    else:
        return include, None
