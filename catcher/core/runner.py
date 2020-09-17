import os
import traceback
from os.path import join

from catcher.core.var_holder import VariablesHolder
from catcher.core.parser import Parser
from catcher.core.step_factory import StepFactory
from catcher.core.test import Test
from catcher.core.filters_factory import FiltersFactory
from catcher.modules.log_storage import LogStorage
from catcher.steps.step import SkipException
from catcher.utils import logger
from catcher.utils.file_utils import cut_path
from catcher.utils.logger import warning, info, debug, OptionalOutput
from catcher.core.mod_factory import ModulesFactory


class Runner:
    def __init__(self,
                 path: str,
                 tests_path: str,
                 inventory: str or None,
                 modules=None,
                 cmd_env=None,
                 system_environment=None,
                 resources=None,
                 output_format=None,
                 filter_list=None) -> None:
        # singletons init should be done before services, as singletons maybe used there
        FiltersFactory(custom_modules=filter_list)
        StepFactory(modules)
        ModulesFactory(resources_dir=resources or os.path.join(path, 'resources'))

        self.tests_path = tests_path
        self.path = path
        self.parser = Parser(path, inventory)
        self.var_holder = VariablesHolder(path,
                                          system_environment=system_environment,
                                          inventory_vars=self.parser.read_inventory(),
                                          cmd_env=cmd_env,
                                          resources=resources)
        if output_format:
            logger.log_storage = LogStorage(output_format)

    def run_tests(self, output: str = 'full') -> bool:
        """
        Run the testcase
        :param output: 'full' - all output possible. 'limited' - only test end report & summary. 'final' - only summary.
        """
        try:
            [mod.before() for mod in ModulesFactory().modules.values()]
            results = []
            for parse_result in self.parser.read_tests(self.tests_path):
                if parse_result.should_run:  # parse successful
                    variables = self.var_holder.variables  # each test has it's own copy of global variables
                    variables['TEST_NAME'] = parse_result.test.file  # variables are shared between test and includes
                    with OptionalOutput(output == 'final'):
                        for include in parse_result.run_on_include:  # run all includes before the main test.
                            self._run_test(include, variables, output=output, test_type='include')
                        result = self._run_test(parse_result.test, variables, output=output)
                        results.append(result)
                        self._run_finally(parse_result.test, result)
                else:  # parse failed (dependency/parsing problem)
                    warning('Test ' + cut_path(self.tests_path, parse_result.test) +
                            logger.red(' failed: ') + str(parse_result.parse_error))
                    logger.log_storage.test_parse_fail(parse_result.test, parse_result.parse_error)
                    results.append(False)
            return all(results)
        finally:
            logger.log_storage.write_report(join(self.path, 'reports'))
            logger.log_storage.print_summary(self.tests_path)
            [mod.after() for mod in ModulesFactory().modules.values()]

    def _run_test(self, test: Test, global_variables: dict, output: str = 'full', test_type='test') -> bool:
        try:
            self.var_holder.prepare_variables(test, global_variables)
            logger.log_storage.test_start(test.file, test_type=test_type)
            test.check_ignored()
            with OptionalOutput(output == 'limited'):
                test.run()
            info(test_type.capitalize() + ' ' + cut_path(self.tests_path, test.file) + logger.green(' passed.'))
            logger.log_storage.test_end(test.file, True, test_type=test_type)
            return True
        except SkipException:
            info(test_type.capitalize() + ' ' + cut_path(self.tests_path, test.file) + logger.yellow(' skipped.'))
            logger.log_storage.test_end(test.file, True, end_comment='Skipped', test_type=test_type)
            return True
        except Exception as e:
            warning(test_type.capitalize() + ' ' + cut_path(self.tests_path, test.file) +
                    logger.red(' failed: ') + str(e))
            debug(traceback.format_exc())
            logger.log_storage.test_end(test.file, False, str(e), test_type=test_type)
            return False

    def _run_finally(self, test, result: bool):
        if test and test.final:
            logger.log_storage.test_start(test.file, test_type='{}_cleanup'.format(test.file))
            try:
                test.run_finally(result)
                info('Test ' + cut_path(self.tests_path, test.file) + ' [cleanup] ' + logger.green(' passed.'))
                logger.log_storage.test_end(test.file, True, test_type='{} [cleanup]'.format(test.file))
            except Exception as e:
                warning('Test ' + cut_path(self.tests_path, test.file) + ' [cleanup] ' +
                        logger.red(' failed: ') + str(e))
                debug(traceback.format_exc())
                logger.log_storage.test_end(test.file, False, test_type='{} [cleanup]'.format(test.file))
