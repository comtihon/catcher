from os.path import join

from catcher.core.include import Include
from catcher.core.test import Test
from catcher.utils.file_utils import read_yaml_file, get_files
from catcher.utils.misc import merge_two_dicts
from catcher.utils.logger import warning


class Runner:
    def __init__(self, path: str, tests_path: str, inventory: str or None) -> None:
        self._tests_path = tests_path
        self._path = path
        self._inventory = inventory
        self._all_includes = []

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

    @all_includes.setter
    def all_includes(self, all_includes: list):
        self._all_includes = all_includes

    def run_tests(self) -> bool:
        variables = {}
        if self.inventory is not None:
            variables = read_yaml_file(self.inventory)
        test_files = get_files(self.tests_path)
        results = []
        for file in test_files:
            self.all_includes = []
            test = self.prepare_test(file, variables)
            try:
                result, _ = test.run()
                results.append(result)
            except Exception:
                warning('test ' + file + ' failed')
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
                    body.get('steps', []))

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
            result, new_vars = include.test.run()
            if not result and not include.ignore_errors:
                raise Exception('Include ' + include.file + ' failed.')
            return new_vars
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
