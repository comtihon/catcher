import traceback

from catcher.core import step_factory
from catcher.steps.step import Step, SkipException
from catcher.steps.stop import StopException
from catcher.utils import logger
from catcher.utils.logger import debug, info
from catcher.utils.misc import fill_template_str, merge_two_dicts


class Test:
    """
    Testcase. Contains variables, includes and steps to run.
    """

    def __init__(self, path: str, includes: dict, variables: dict,
                 config: dict, steps: list, final: list, modules: dict, override_vars=None) -> None:
        self.includes = includes
        self.variables = variables
        self.config = config
        self.steps = steps
        self.path = path
        self.modules = modules
        self.final = final
        self.override_vars = override_vars if override_vars is not None else {}

    def run(self, tag=None, raise_stop=False) -> dict:
        for step in self.steps:
            if not self._run_step(step, tag, raise_stop):
                break
        return self.variables

    def run_finally(self, result: bool):
        for step in self.final:
            if not self._run_step(step, result=result):
                return

    def _run_step(self, step, tag=None, raise_stop=False, result=None) -> bool:
        [action] = step.keys()
        ignore_errors = get_or_default('ignore_errors', step[action], False)
        if tag is not None:  # skip if tag specified
            step_tag = get_or_default('tag', step[action], None)
            if step_tag != tag:
                return True
        if result is not None:  # skip if result is specified (step is final)
            run_type = get_or_default('run', step[action], 'always')
            if (not result and run_type == 'pass') or (result and run_type == 'fail'):
                debug('Skip final action')
                return True
        actions = step_factory.get_actions(self.path, step, self.modules)
        for action_object in actions:
            # override all variables with cmd variables
            variables = merge_two_dicts(self.variables, self.override_vars)
            if not self._run_actions(step, action, action_object, variables, raise_stop, ignore_errors):
                return False
        return True

    def _run_actions(self, step, action, action_object, variables, raise_stop, ignore_errors) -> bool:
        action_name = get_action_name(action, action_object, variables)
        try:
            logger.log_storage.new_step(step, variables)
            action_object.check_skip(variables)
            self.variables = action_object.action(self.includes, variables)
            # repeat for run (variables were computed after name)
            action_name = get_action_name(action, action_object, self.variables)
            info('Step ' + action_name + logger.green(' OK'))
            logger.log_storage.step_end(step, self.variables)
            return True
        except StopException as e:  # stop a test without error
            if raise_stop:  # or raise error if configured
                logger.log_storage.step_end(step, variables, success=False, output=str(e))
                raise e
            debug('Skip ' + action_name + ' due to ' + str(e))
            info('Step ' + action_name + logger.green(' OK'))
            logger.log_storage.step_end(step, self.variables, success=True, output=str(e))
            return False  # stop current test
        except SkipException as e:  # skip this step
            info('Step ' + action_name + logger.yellow(' skipped'))
            logger.log_storage.step_end(step, self.variables, success=True, output=str(e))
            return True
        except Exception as e:
            if ignore_errors:  # continue actions & steps execution
                debug('Step ' + action_name + logger.red(' failed') + ', but we ignore it')
                logger.log_storage.step_end(step, variables, success=True)
                return True
            else:
                info('Step ' + action_name + logger.red(' failed: ') + str(e))
                debug(traceback.format_exc())
                logger.log_storage.step_end(step, variables, success=False, output=str(e))
                raise e

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
