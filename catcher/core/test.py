import traceback

from catcher.steps import step_factory
from catcher.steps.step import Step
from catcher.steps.stop import StopException
from catcher.utils.logger import debug, info
from catcher.utils.misc import fill_template_str


class Test:
    def __init__(self, path: str, includes: dict, variables: dict, config: dict, steps: list, modules: dict) -> None:
        self._includes = includes
        self._variables = variables
        self._config = config
        self._steps = steps
        self._path = path
        self.__modules = modules

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

    @property
    def modules(self) -> dict:
        return self.__modules

    def run(self, tag=None, raise_stop=False) -> dict:
        for step in self.steps:
            [action] = step.keys()
            ignore_errors = get_or_default('ignore_errors', step[action], False)
            if tag is not None:
                step_tag = get_or_default('tag', step[action], None)
                if step_tag != tag:
                    continue
            actions = step_factory.get_actions(self.path, step, self.modules)
            for action_object in actions:
                action_name = get_action_name(action, action_object, self.variables)
                try:
                    self.variables = action_object.action(self.includes, self.variables)
                    info('Step ' + action_name + ' OK')
                except StopException as e:
                    if raise_stop:
                        raise e
                    debug('Skip ' + action_name + ' due to ' + str(e))
                    info('Step ' + action_name + ' OK')
                    return self.variables  # stop current test
                except Exception as e:
                    print(traceback.format_exc())
                    if ignore_errors:
                        debug('Step ' + action_name + ' failed, but we ignore it')
                        continue
                    info('Step ' + action_name + ' failed: ' + str(e))
                    raise e
        return self.variables


def get_or_default(key: str, body: dict or str, default: any) -> any:
    if isinstance(body, dict):
        return body.get(key, default)
    else:
        return default


def get_action_name(action_type: str, action: Step, variables: dict):
    if action.name is not None:
        return fill_template_str(action.name, variables)
    return action_type
