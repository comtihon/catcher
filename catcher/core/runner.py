import traceback
from os.path import join

from catcher.core.parser import Parser
from catcher.core.test import Test
from catcher.modules.compose import DockerCompose
from catcher.modules.filters import FiltersHolder
from catcher.modules.log_storage import LogStorage
from catcher.steps import step
from catcher.steps.step import SkipException
from catcher.utils import logger
from catcher.utils.logger import warning, info, debug, VariableOutput
from catcher.utils.misc import merge_two_dicts, try_get_object, fill_template_str, report_override
from catcher.utils.module_utils import prepare_modules
from catcher.core.step_factory import StepFactory


class Runner:
    def __init__(self,
                 path: str,
                 tests_path: str,
                 inventory: str or None,
                 modules=None,
                 environment=None,
                 system_environment=None,
                 resources=None,
                 output_format=None,
                 filter_list=None) -> None:
        if modules is None:
            modules = []
        self.environment = environment if environment is not None else {}
        self.tests_path = tests_path
        self.path = path
        self.all_includes = None
        self._compose = DockerCompose(resources)
        self.resources = resources
        self.parser = Parser(path, inventory, environment, resources, system_environment)
        if output_format:
            logger.log_storage = LogStorage(output_format)
        FiltersHolder(filter_list)
        StepFactory(merge_two_dicts(prepare_modules(modules, step.registered_steps), step.registered_steps))

    def run_tests(self, output: str = 'full') -> bool:
        """
        Run the testcase
        :param output: 'full' - all output possible. 'limited' - only test end report & summary. 'final' - only summary.
        """
        try:
            self._compose.up()
            results = []
            for run_includes, test in self.parser.read_tests(self.tests_path):
                variables = self.parser.variables  # each test has it's own copy of global variables
                variables['TEST_NAME'] = test.file  # variables are shared between test and includes
                with VariableOutput(output == 'final'):
                    for include in run_includes:  # run all includes before the main test.
                        self._run_include(include, variables, output=output)
                    result = self._run_test(test, variables, output=output)
                    results.append(result)
                    self._run_finally(test, result)
            return all(results)
        finally:
            logger.log_storage.write_report(join(self.path, 'reports'))
            logger.log_storage.print_summary(self.tests_path)
            self._compose.down()

    @staticmethod
    def _run_include(test: Test, global_variables: dict, output: str = 'full') -> bool:
        Runner._update_variables(test.variables, global_variables, test.include.variables)
        test.variables = global_variables
        try:
            logger.log_storage.test_start(test.file, test_type='include')
            debug('Run include: ' + str(test))
            with VariableOutput(output == 'limited'):
                res = test.run()
            logger.log_storage.test_end(test.file, True, res, test_type='include')
            return True
        except SkipException:
            info('Include ' + test.file + logger.yellow(' skipped.'))
            logger.log_storage.test_end(test.file, True, end_comment='Skipped')
            return True
        except Exception as e:
            logger.log_storage.test_end(test.file, False, str(e), test_type='include')
            if not test.include.ignore_errors:
                raise Exception('Include ' + test.file + ' failed: ' + str(e))
            return False

    @staticmethod
    def _run_test(test: Test, global_variables: dict, output: str = 'full') -> bool:
        Runner._update_variables(test.variables, global_variables)
        test.variables = global_variables
        try:
            logger.log_storage.test_start(test.file)
            test.check_ignored()
            with VariableOutput(output == 'limited'):
                test.run()
            info('Test ' + test.file + logger.green(' passed.'))
            logger.log_storage.test_end(test.file, True)
            return True
        except SkipException:
            info('Test ' + test.file + logger.yellow(' skipped.'))
            logger.log_storage.test_end(test.file, True, end_comment='Skipped')
            return True
        except Exception as e:
            warning('Test ' + test.file + logger.red(' failed: ') + str(e))
            debug(traceback.format_exc())
            logger.log_storage.test_end(test.file, False, str(e))
            return False

    @classmethod
    def _run_finally(cls, test, result: bool):
        if test and test.final:
            logger.log_storage.test_start(test.file, test_type='{}_cleanup'.format(test.file))
            try:
                test.run_finally(result)
                info('Test ' + test.file + ' [cleanup] ' + logger.green(' passed.'))
                logger.log_storage.test_end(test.file, True, test_type='{} [cleanup]'.format(test.file))
            except Exception as e:
                warning('Test ' + test.file + ' [cleanup] ' + logger.red(' failed: ') + str(e))
                debug(traceback.format_exc())
                logger.log_storage.test_end(test.file, False, test_type='{} [cleanup]'.format(test.file))

    @staticmethod
    def _update_variables(body_vars, global_variables, override_vars=None):
        """
        Create variables for test
        :param body_vars: variables specified at test's header
        :param global_variables: variables from inventory + env vars (if enabled) + variables from includes
        :param override_vars: variables which override body_vars in case this test is included
        :return: final variables
        """
        tests_variables = try_get_object(fill_template_str(body_vars, global_variables))
        global_variables.update(tests_variables)
        if override_vars:
            override_keys = report_override(global_variables, override_vars)
            if override_keys:
                debug('Overriding these variables: ' + str(override_keys))
            global_variables.update(override_vars)
