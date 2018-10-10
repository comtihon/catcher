from os.path import join

from catcher.core.test import Test, Include
from catcher.steps import step
from catcher.utils.file_utils import get_files, read_source_file
from catcher.utils.logger import warning, info
from catcher.utils.misc import merge_two_dicts, try_get_object, fill_template_str
from catcher.utils.module_utils import prepare_modules


class Runner:
    def __init__(self, path: str, tests_path: str, inventory: str or None, modules=None, environment=None) -> None:
        if modules is None:
            modules = []
        self.environment = environment if environment is not None else {}
        self.tests_path = tests_path
        self.path = path
        self.inventory = inventory
        self.all_includes = []
        self.modules = merge_two_dicts(prepare_modules(modules, step.registered_steps), step.registered_steps)

    def run_tests(self) -> bool:
        variables = {}
        if self.inventory is not None:
            variables = read_source_file(self.inventory)
            variables = try_get_object(fill_template_str(variables, {}))  # fill env vars
        test_files = get_files(self.tests_path)
        results = []
        for file in test_files:
            self.all_includes = []
            try:
                variables['TEST_NAME'] = file
                test = self.prepare_test(file, variables)
                test.run()
                results.append(True)
                info('Test ' + file + ' passed.')
            except Exception as e:
                warning('Test ' + file + ' failed: ' + str(e))
                results.append(False)
        return all(results)

    def prepare_test(self, file: str, variables: dict, override_vars: None or dict = None) -> Test:
        body = read_source_file(file)
        registered_includes = self.process_includes(body.get('include', []), variables)
        variables = merge_two_dicts(variables, body.get('variables', {}))  # override variables with test's variables
        if override_vars:  # TODO warn when overriding inventory vars?
            variables = merge_two_dicts(variables, override_vars)
        return Test(self.path,
                    registered_includes,
                    variables,
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
                return include.test.run()
            except Exception as e:
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
