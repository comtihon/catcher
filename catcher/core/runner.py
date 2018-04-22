import os
from os.path import join

from catcher.core.include import Include
from catcher.core.test import Test
from catcher.utils.file_utils import read_yaml_file, get_files
from catcher.utils.logger import warning, info, error
from catcher.utils.misc import merge_two_dicts


class Runner:
    def __init__(self, path: str, tests_path: str, inventory: str or None, modules=None) -> None:
        if modules is None:
            modules = []
        self._tests_path = tests_path
        self._path = path
        self._inventory = inventory
        self._all_includes = []
        self.__prepare_modules(modules)

    @property
    def tests_path(self) -> str:
        return self._tests_path

    @property
    def path(self) -> str:
        return self._path

    @property
    def inventory(self) -> str or None:
        return self._inventory

    @property
    def all_includes(self) -> list:
        return self._all_includes

    @property
    def modules(self) -> dict:
        return self._modules

    @all_includes.setter
    def all_includes(self, all_includes: list):
        self._all_includes = all_includes

    def run_tests(self, override_variables=None) -> bool:
        if override_variables is None:
            override_variables = {}
        variables = {}
        if self.inventory is not None:
            variables = read_yaml_file(self.inventory)
        variables = merge_two_dicts(variables, override_variables)  # override inventory variables with cmd variables
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
        body = read_yaml_file(file)
        registered_includes = self.process_includes(body.get('include', []), variables)
        variables = merge_two_dicts(variables, body.get('variables', {}))  # override variables with test's variables
        if override_vars:  # TODO warn when overriding inventory vars?
            variables = merge_two_dicts(variables, override_vars)
        return Test(self.path,
                    registered_includes,
                    variables,
                    body.get('config', {}),
                    body.get('steps', []),
                    self.modules)

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

    def __prepare_modules(self, module_paths: list):
        indexed = {}
        for path in module_paths:
            if not os.path.exists(path):
                err = 'No such path: ' + path
                error(err)
            else:
                for f in os.listdir(path):
                    mod_path = join(path, f)
                    if f in indexed:
                        warning('Override ' + indexed[f] + ' with ' + mod_path)
                    indexed[f] = mod_path
        self._modules = indexed
