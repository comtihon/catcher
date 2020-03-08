from copy import deepcopy
from os.path import join

from catcher.utils import logger
from catcher.core.test import Test, Include
from catcher.modules.compose import DockerCompose
from catcher.steps import step
from catcher.utils.file_utils import get_files, read_source_file, get_filename
from catcher.utils.logger import warning, info, debug
from catcher.utils.misc import merge_two_dicts, try_get_object, fill_template_str, report_override
from catcher.utils.module_utils import prepare_modules
from catcher.modules.log_storage import LogStorage


class Runner:
    def __init__(self,
                 path: str,
                 tests_path: str,
                 inventory: str or None,
                 modules=None,
                 environment=None,
                 system_environment=None,
                 resources=None,
                 output_format=None) -> None:
        if modules is None:
            modules = []
        self.environment = environment if environment is not None else {}
        self.system_vars = system_environment if system_environment is not None else {}
        self.tests_path = tests_path
        self.path = path
        self.inventory = inventory
        self.all_includes = []
        self.modules = merge_two_dicts(prepare_modules(modules, step.registered_steps), step.registered_steps)
        self._compose = DockerCompose(resources)
        self.resources = resources
        if output_format:
            logger.log_storage = LogStorage(output_format)

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
                self.all_includes = []
                try:
                    variables['TEST_NAME'] = file
                    test = self.prepare_test(file, variables)
                    logger.log_storage.test_start(file)
                    test.run()
                    results.append(True)
                    info('Test ' + file + ' passed.')
                    logger.log_storage.test_end(file, True)
                except Exception as e:
                    warning('Test ' + file + ' failed: ' + str(e))
                    results.append(False)
                    logger.log_storage.test_end(file, False, str(e))
            return all(results)
        finally:
            logger.log_storage.write_report(join(self.path, 'reports'))
            self._compose.down()

    def prepare_test(self, file: str, variables: dict, override_vars: None or dict = None) -> Test:
        body = read_source_file(file)
        registered_includes = self.process_includes(body.get('include', []), variables)
        tests_variables = try_get_object(fill_template_str(body.get('variables', {}),
                                                           merge_two_dicts(variables, self.environment)))
        variables = merge_two_dicts(variables, tests_variables)  # override variables with test's variables
        if override_vars:
            override_keys = report_override(variables, override_vars)
            if override_keys:
                debug('Overriding these variables: ' + str(override_keys))
            variables = merge_two_dicts(variables, override_vars)
        return Test(self.path,
                    registered_includes,
                    deepcopy(variables),  # each test has independent variables
                    body.get('config', {}),
                    body.get('steps', []),
                    self.modules,
                    self.environment)

    def process_includes(self,
                         includes: list or str or dict,
                         variables: dict,
                         registered_includes: dict or None = None) -> (dict, dict):
        if registered_includes is None:
            registered_includes = {}
        if isinstance(includes, str) or isinstance(includes, dict):  # single include
            self.process_include(includes, registered_includes, variables)
        elif isinstance(includes, list):  # an array of includes
            for i in includes:  # run all includes and save includes with alias
                variables = self.process_include(i, registered_includes, variables)
        return registered_includes

    def process_include(self, include_file: str or dict, includes: dict, variables: dict) -> dict:
        include_file = self.path_from_root(include_file)
        self.check_circular(include_file)
        include = Include(**include_file)
        self.all_includes.append(include)
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

    def check_circular(self, current_include: dict):
        path = current_include['file']
        if [include for include in self.all_includes if include.file == path]:
            raise Exception('Circular dependencies for ' + path)

    def path_from_root(self, include_file: str or dict) -> dict:
        if isinstance(include_file, str):
            return {'file': join(self.path, include_file)}
        else:
            include_file['file'] = join(self.path, include_file['file'])
            return include_file
