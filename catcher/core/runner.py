import traceback
from copy import deepcopy
from os.path import join

from catcher.core.include import Include
from catcher.core.test import Test
from catcher.modules.compose import DockerCompose
from catcher.modules.filters import FiltersHolder
from catcher.modules.log_storage import LogStorage
from catcher.steps import step
from catcher.utils import logger
from catcher.utils.file_utils import get_files, read_source_file, get_filename
from catcher.utils.logger import warning, info, debug
from catcher.utils.misc import merge_two_dicts, try_get_object, fill_template_str, report_override
from catcher.utils.module_utils import prepare_modules


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
        self.system_vars = system_environment if system_environment is not None else {}
        self.tests_path = tests_path
        self.path = path
        self.inventory = inventory
        self.all_includes = None
        self.modules = merge_two_dicts(prepare_modules(modules, step.registered_steps), step.registered_steps)
        self._compose = DockerCompose(resources)
        self.resources = resources
        if output_format:
            logger.log_storage = LogStorage(output_format)
        FiltersHolder(filter_list)

    def run_tests(self) -> bool:
        try:
            self._compose.up()
            if self.system_vars:
                debug('Use system variables: ' + str(list(self.system_vars.keys())))
                variables = self.system_vars
            else:
                variables = {}
            if self.inventory is not None:
                inv_vars = read_source_file(self.inventory)
                inv_vars['INVENTORY'] = get_filename(self.inventory)
                inv_vars['INVENTORY_FILE'] = self.inventory
                variables = try_get_object(fill_template_str(inv_vars, variables))  # fill env vars
            variables['CURRENT_DIR'] = self.path
            variables['RESOURCES_DIR'] = self.resources or self.path + '/resources'
            test_files = get_files(self.tests_path)
            results = []
            for file in test_files:
                self.all_includes = None  # each test has it's own include tree
                variables['TEST_NAME'] = file
                test, result = self._run_test(file, variables)
                results.append(result)
                self._run_finally(test, file, result)
            return all(results)
        finally:
            logger.log_storage.write_report(join(self.path, 'reports'))
            self._compose.down()

    def prepare_test(self, file: str, variables: dict, override_vars: None or dict = None) -> Test:
        body = read_source_file(file)
        registered_includes = self.process_includes(file, body.get('include', []), variables)
        tests_variables = try_get_object(fill_template_str(body.get('variables', {}),
                                                           merge_two_dicts(variables, self.environment)))
        variables = merge_two_dicts(variables, tests_variables)  # override variables with test's variables
        if override_vars:
            override_keys = report_override(variables, override_vars)
            if override_keys:
                debug('Overriding these variables: ' + str(override_keys))
            variables = merge_two_dicts(variables, override_vars)
        return Test(self.path,
                    includes=registered_includes,
                    variables=deepcopy(variables),  # each test has independent variables
                    config=body.get('config', {}),
                    steps=body.get('steps', []),
                    final=body.get('finally', []),
                    modules=self.modules,
                    override_vars=self.environment)

    def process_includes(self,
                         file: str,
                         includes: list or str or dict,
                         variables: dict,
                         registered_includes: dict or None = None) -> (dict, dict):
        if registered_includes is None:
            registered_includes = {}
        if isinstance(includes, str) or isinstance(includes, dict):  # single include
            self.process_include(file, includes, registered_includes, variables)
        elif isinstance(includes, list):  # an array of includes
            for i in includes:  # run all includes and save includes with alias
                variables = self.process_include(file, i, registered_includes, variables)
        return registered_includes

    def process_include(self, parent: str, include_file: str or dict, includes: dict, variables: dict) -> dict:
        include_file = self.path_from_root(include_file)
        self.all_includes, include = Include.check_circular(parent, self.all_includes, include_file)
        include.test = self.prepare_test(include.file, variables, include.variables)
        if include.alias is not None:
            includes[include.alias] = include.test
        if include.run_on_include:
            try:
                logger.log_storage.test_start(include_file['file'], test_type='include')
                debug('Run include: ' + str(include.test))
                res = include.test.run()
                logger.log_storage.test_end(include.test.path, True, res, test_type='include')
                return res
            except Exception as e:
                logger.log_storage.test_end(include.test.path, False, str(e), test_type='include')
                if not include.ignore_errors:
                    raise Exception('Include ' + include.file + ' failed: ' + str(e))
        return include.test.variables

    def path_from_root(self, include_file: str or dict) -> dict:
        if isinstance(include_file, str):
            return {'file': join(self.path, include_file)}
        else:
            include_file['file'] = join(self.path, include_file['file'])
            return include_file

    def _run_test(self, file, variables):
        test = None
        try:
            test = self.prepare_test(file, variables)
            logger.log_storage.test_start(file)
            test.run()
            info('Test ' + file + logger.green(' passed.'))
            logger.log_storage.test_end(file, True)
            return test, True
        except Exception as e:
            warning('Test ' + file + logger.red(' failed: ') + str(e))
            debug(traceback.format_exc())
            logger.log_storage.test_end(file, False, str(e))
            return test, False

    @classmethod
    def _run_finally(cls, test, file, result: bool):
        if test and test.final:
            logger.log_storage.test_start(file, test_type='{}_cleanup'.format(file))
            try:
                test.run_finally(result)
                info('Test ' + file + ' [cleanup] ' + logger.green(' passed.'))
                logger.log_storage.test_end(file, True, test_type='{} [cleanup]'.format(file))
            except Exception as e:
                warning('Test ' + file + ' [cleanup] ' + logger.red(' failed: ') + str(e))
                debug(traceback.format_exc())
                logger.log_storage.test_end(file, False, test_type='{} [cleanup]'.format(file))
