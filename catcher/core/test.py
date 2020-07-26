import time
import traceback
from typing import Union

from catcher.steps.step import Step, SkipException
from catcher.steps.stop import StopException
from catcher.utils import logger
from catcher.utils.logger import debug, info
from catcher.utils.misc import fill_template_str
from catcher.steps.check import Operator
from catcher.core.step_factory import StepFactory


class Test:
    """
    Testcase. Contains variables, includes, steps and final actions.

    :ignore: if true will ignore this test. A condition based on :meth:`catcher.steps.check.Check` can be used to
     compute ignore condition dynamically.

    :include: other test to run. See :meth:`catcher.core.include.Include`. Can be a string in case of single
      include or a list of include in case of multiple. Each of them will be run before the test passing variables to
      each other and, finally, to the test. In case of `run_on_include` include's property is false or `as` alias is set
      include won't be run before the test. You can run such include via :meth:`catcher.steps.run.Run` step later.
      See :doc:`includes` for more info.

    :variables: test local variables which override inventory variables. These variables will be available only in this
     test or in test which includes this test. Variables itself can contain templates.
     See :doc:`variables` for more info.

    :steps: A list of test actions which will be run one by one. They can use variables and support templates. Each
     step can register it's output as a new variable. See :meth:`catcher.steps.step.Step` for available options.
     See :doc:`internal_modules` and `external modules <https://catcher-modules.readthedocs.io/en/latest/index.html>`_
     for more info.

    :finally: A list of clean up actions which will be run after test finishes execution. Condition for every clean up
     action run can be set (by default they run in any case).

    See :doc:`tests` for more info and examples.

    """

    def __init__(self,
                 path: str,
                 file: str,
                 includes: dict = None,
                 variables: dict = None,
                 config: dict = None,
                 steps: list = None,
                 final: list = None,
                 ignore: Union[bool, str, dict] = None) -> None:
        self.path = path
        self.final = final
        self.file = file
        self.includes = includes
        self.config = config
        self.variables = variables
        self.steps = steps
        self.ignore = ignore
        self.include = None  # if this test is include it will refer to `Include` class

    def check_ignored(self):
        if self.ignore:
            if not isinstance(self.ignore, bool):
                self.ignore = Operator.find_operator(self.ignore).operation(self.variables)
            if self.ignore:
                raise SkipException('Test ignored')

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
            run_type = get_or_default('run_if', step[action], 'always')
            if (not result and run_type == 'pass') or (result and run_type == 'fail'):
                debug('Skip final action')
                return True
        actions = StepFactory().get_actions(self.path, step)
        for action_object in actions:
            # override all variables with cmd variables
            if not self._run_actions(step, action, action_object, self.variables, raise_stop, ignore_errors):
                return False
        return True

    def _run_actions(self, step, action, action_object, variables, raise_stop, ignore_errors) -> bool:
        action_name = get_action_name(action, action_object, variables)
        start = time.process_time()
        try:
            logger.log_storage.new_step(step, variables)
            action_object.check_skip(variables)
            self.variables = action_object.action(self.includes, variables)
            # repeat for run (variables were computed after name)
            action_name = get_action_name(action, action_object, self.variables)
            info('Step ' + action_name + get_timing(start) + logger.green(' OK'))
            logger.log_storage.step_end(step, self.variables)
            return True
        except StopException as e:  # stop a test without error
            if raise_stop:  # or raise error if configured
                logger.log_storage.step_end(step, variables, success=False, output=str(e))
                raise e
            debug('Skip ' + action_name + ' due to ' + str(e))
            info('Step ' + action_name + get_timing(start) + logger.green(' OK'))
            logger.log_storage.step_end(step, self.variables, success=True, output=str(e))
            return False  # stop current test
        except SkipException as e:  # skip this step
            info('Step ' + action_name + logger.yellow(' skipped'))
            logger.log_storage.step_end(step, self.variables, success=True, output=str(e))
            return True
        except Exception as e:
            if ignore_errors:  # continue actions & steps execution
                debug('Step ' + action_name + get_timing(start) + logger.red(' failed') + ', but we ignore it')
                logger.log_storage.step_end(step, variables, success=True)
                return True
            else:
                info('Step ' + action_name + get_timing(start) + logger.red(' failed: ') + str(e))
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


def get_timing(start_time) -> str:
    delta = time.process_time() - start_time
    if delta > 60:
        return ' [{:.0f}m {:.0f}s]'.format(delta / 60, delta - 60 * int(delta / 60))
    return ' [{:.0f}s]'.format(delta)
