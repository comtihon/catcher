import os
from copy import deepcopy
from typing import Optional, Tuple, List

from catcher.utils.logger import debug
from catcher.utils.file_utils import read_source_file, get_filename, get_files
from catcher.utils.misc import try_get_object, fill_template_str
from catcher.core.include import Include
from catcher.core.test import Test


class Parser:

    def __init__(self,
                 path: str,
                 inventory: Optional[str],
                 environment: Optional[dict] = None,
                 resources: Optional[dict] = None,
                 system_environment=None) -> None:
        self.path = path
        self.environment = environment or {}
        system_vars = system_environment or {}
        if system_vars:
            debug('Use system variables: ' + str(list(system_vars.keys())))
            self._variables = system_vars
        else:
            self._variables = {}
        self._variables = self.read_inventory(inventory)
        self._variables['CURRENT_DIR'] = self.path
        self._variables['RESOURCES_DIR'] = resources or os.path.join(self.path, 'resources')

    @property
    def variables(self) -> dict:
        return deepcopy(self._variables)

    def read_inventory(self, inventory: Optional[str]) -> dict:
        if inventory is not None:
            inv_vars = read_source_file(inventory)
            inv_vars['INVENTORY'] = get_filename(inventory)
            inv_vars['INVENTORY_FILE'] = inventory
            return try_get_object(fill_template_str(inv_vars, self._variables))  # fill env vars
        return {}

    def read_tests(self, test_path: str) -> List[Tuple[List[Test], Test]]:
        """
        Parse all tests at path, return pairs of (tests run before the test, test)
        """
        results = []
        for test_file in get_files(test_path):
            raw_test = self.read_test(test_file)
            run_on_include = self.fill_includes_recursive(test_file, raw_test, None)
            results += [(run_on_include, raw_test)]
        return results

    def fill_includes_recursive(self, parent, raw_test, all_includes):
        run_on_include = []
        all_includes, raw_includes = Include.read_includes(self.path, parent, raw_test.includes, all_includes)
        raw_test.includes = {}  # clear & fill real includes
        for include in raw_includes:
            test = self.read_test(include.file)
            test.include = include  # remember include's properties (like ignore_errors)
            if include.alias is not None:
                raw_test.includes[include.alias] = test
            if include.run_on_include:
                run_on_include += [test]
            return run_on_include + self.fill_includes_recursive(include.file, test, all_includes)
        return run_on_include

    def read_test(self, test_file: str):
        body = read_source_file(test_file)
        return Test(self.path,
                    test_file,
                    includes=body.get('include', []),
                    variables=body.get('variables', {}),
                    config=body.get('config', {}),
                    steps=body.get('steps', []),
                    final=body.get('finally', []),
                    ignore=body.get('ignore', False))
