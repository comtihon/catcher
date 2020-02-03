import traceback

from catcher.utils import logger

from catcher.steps.step import Step
from catcher.steps.stop import StopException
from catcher.utils.logger import debug, info
from catcher.utils.misc import fill_template_str, merge_two_dicts
from catcher.core import step_factory


class Include:
    """
    Include another testcase in include section:

    ::
        include:
            - file: simple_file.yaml
              run_on_include: false
            - other_simple_file.yaml

    each include file has it's own Include object and attached Test
    """

    def __init__(self, ignore_errors=False, **keywords) -> None:
        if 'file' not in keywords:
            raise RuntimeError('Can\'t include unknown file.')
        self.file = keywords['file']
        self.variables = keywords.get('variables', {})
        self.alias = keywords.get('as', None)
        self.run_on_include = keywords.get('run_on_include', self.alias is None)
        self.ignore_errors = ignore_errors
        self.test = None


class Test:
    """
    Testcase. Contains variables, includes and steps to run.
    """

    def __init__(self, path: str, includes: dict, variables: dict,
                 config: dict, steps: list, modules: dict, override_vars=None) -> None:
        self.includes = includes
        self.variables = variables
        self.config = config
        self.steps = steps
        self.path = path
        self.modules = modules
        self.override_vars = override_vars if override_vars is not None else {}

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
                # override all variables with cmd variables
                variables = merge_two_dicts(self.variables, self.override_vars)
                action_name = get_action_name(action, action_object, variables)
                try:
                    logger.log_storage.new_step(step, variables)
                    self.variables = action_object.action(self.includes, variables)
                    # repeat for run (variables were computed after name)
                    action_name = get_action_name(action, action_object, self.variables)
                    info('Step ' + action_name + ' OK')
                    logger.log_storage.step_end(step, self.variables)
                except StopException as e:  # stop a test without error
                    if raise_stop:  # or raise error if configured
                        logger.log_storage.step_end(step, variables, success=False, output=str(e))
                        raise e
                    debug('Skip ' + action_name + ' due to ' + str(e))
                    info('Step ' + action_name + ' OK')
                    logger.log_storage.step_end(step, self.variables, success=True, output=str(e))
                    return self.variables  # stop current test
                except Exception as e:
                    if ignore_errors:
                        debug('Step ' + action_name + ' failed, but we ignore it')
                        logger.log_storage.step_end(step, variables, success=True)
                        continue
                    info('Step ' + action_name + ' failed: ' + str(e))
                    debug(traceback.format_exc())
                    logger.log_storage.step_end(step, variables, success=False, output=str(e))
                    raise e
        return self.variables

    def __repr__(self) -> str:
        return str(self.steps)


def get_or_default(key: str, body: dict or str, default: any) -> any:
    if isinstance(body, dict):
        return body.get(key, default)
    else:
        return default


def get_action_name(action_type: str, action: Step, variables: dict):
    if action.name is not None:
        return fill_template_str(action.name, variables)
    return action_type
