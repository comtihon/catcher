import traceback

from catcher.steps import step_factory
from catcher.utils.logger import debug, warning


class Test:
    def __init__(self, path: str, includes: dict, variables: dict, config: dict, steps: list) -> None:
        self._includes = includes
        self._variables = variables
        self._config = config
        self._steps = steps
        self._path = path

    @property
    def includes(self) -> dict:
        return self._includes

    @property
    def variables(self) -> dict:
        return self._variables

    @variables.setter
    def variables(self, variables):
        self._variables = variables

    @property
    def config(self) -> dict:
        return self._config

    @property
    def steps(self) -> list:
        return self._steps

    @property
    def path(self) -> str:
        return self._path

    def run(self, tag=None) -> {bool, dict}:
        for step in self.steps:
            [action] = step.keys()
            ignore_errors = get_or_default('ignore_errors', step[action], False)
            if tag is not None:
                step_tag = get_or_default('tag', step[action], None)
                if step_tag != tag:
                    continue
            actions = step_factory.get_actions(self.path, step)
            for action_object in actions:
                try:
                    self.variables = action_object.action(self.includes, self.variables)
                except Exception as e:
                    if ignore_errors:
                        debug('Step ' + action + ' failed, but we ignore it')
                        continue
                    print(traceback.format_exc())
                    warning('Step ' + action + ' crashed: ' + str(e))
                    return False, self.variables
        return True, self.variables


def get_or_default(key: str, body: dict or str, default: any) -> any:
    if isinstance(body, dict):
        return body.get(key, default)
    else:
        return default
