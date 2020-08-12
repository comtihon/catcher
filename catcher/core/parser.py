from typing import Optional, List

from catcher.core.include import Include
from catcher.core.test import Test
from catcher.utils.file_utils import read_source_file, get_filename, get_files


class ParseResult:
    def __init__(self, test_to_run, run_on_include=None, parse_error=None) -> None:
        super().__init__()
        self.run_on_include = run_on_include
        self.parse_error = parse_error
        self.test = test_to_run

    @property
    def should_run(self) -> bool:
        return self.parse_error is None


class Parser:

    def __init__(self, path: str, inventory_path: Optional[str]) -> None:
        self.path = path
        self.inventory = inventory_path

    def read_inventory(self) -> dict:
        if self.inventory is not None:
            inv_vars = read_source_file(self.inventory)
            inv_vars['INVENTORY'] = get_filename(self.inventory)
            inv_vars['INVENTORY_FILE'] = self.inventory
            return inv_vars
        return {}

    def read_tests(self, test_path: str) -> List[ParseResult]:
        """
        Parse all tests at path, return pairs of (tests run before the test, test)
        """
        results = []
        for test_file in get_files(test_path):
            try:
                raw_test = self.read_test(test_file)
                if raw_test.ignore:  # ignore the test - do not need to check imports (they may be missing)
                    results += [ParseResult(raw_test, run_on_include=[])]
                    continue
                run_on_include = self.fill_includes_recursive(test_file, raw_test, None)
                results += [ParseResult(raw_test, run_on_include=run_on_include)]
            except Exception as e:
                results += [ParseResult(test_file, parse_error=str(e))]
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
            run_on_include += self.fill_includes_recursive(include.file, test, all_includes)
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
