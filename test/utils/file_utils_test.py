from os.path import join

from catcher.utils.file_utils import ensure_dir, read_yaml_file, get_files
from test.abs_test_class import TestClass


class UtilsTest(TestClass):
    def __init__(self, method_name):
        super().__init__('utils_test', method_name)

    @property
    def yaml_template(self) -> str:
        return '''---
        vars:
            foo: bar
        steps:
            - one
            - two
            - three
        '''

    @property
    def yaml_parsed(self) -> dict:
        return {'steps': ['one', 'two', 'three'], 'vars': {'foo': 'bar'}}

    # read and parse yaml file
    def test_read_yaml_simple(self):
        self.__populate_files(['test_file.yaml'])
        file = join(self.test_dir, 'test_file.yaml')
        result = read_yaml_file(file)
        self.assertEqual(self.yaml_parsed, result)

    # find file, when launched via `catcher /path/to/file.yaml`
    def test_find_one_file(self):
        self.__populate_files(['test_file.yaml'])
        file = join(self.test_dir, 'test_file.yaml')
        result = get_files(file)
        self.assertEqual([file], result)

    # find all files, when launched via `catcher /path/to`
    def test_find_all_in_dir(self):
        files = ['d', 'd/test1.yaml', 'd/test2.yaml']
        self.__populate_files(files)
        result = get_files(join(self.test_dir, 'd'))
        expected = [join(self.test_dir, f) for f in files if f.endswith('yaml')]
        expected.reverse()
        self.assertEqual(sorted(expected), sorted(result))

    # find all files, when launched via `catcher /path/to` with subdirs
    def test_find_all_with_subdir(self):
        files = ['d', 'd/d1', 'd/test1.yaml', 'd/test2.yaml', 'd/d1/test3.yaml']
        self.__populate_files(files)
        result = get_files(join(self.test_dir, 'd'))
        expected = [join(self.test_dir, f) for f in files if f.endswith('yaml')]
        expected.reverse()
        self.assertEqual(sorted(expected), sorted(result))

    # find all files, when launched via `catcher /path/to` with subdirs and other files
    def test_find_all_filter_unknown(self):
        files = ['d', 'd/d1', 'd/test1.yaml', 'd/test2.yaml', 'd/d1/test3.yaml']
        self.__populate_files(files)
        with open(join(self.test_dir, 'd/Readme.md'), 'w') as f:
            f.write('first_readme')
        with open(join(self.test_dir, 'd/d1/Readme.md'), 'w') as f:
            f.write('second_readme')
        result = get_files(join(self.test_dir, 'd'))
        expected = [join(self.test_dir, f) for f in files if f.endswith('yaml')]
        expected.reverse()
        self.assertEqual(sorted(expected), sorted(result))

    def __populate_files(self, files):
        for file in files:
            if file.endswith('.yaml'):
                with open(join(self.test_dir, file), 'w') as f:
                    f.write(str(self.yaml_template))
            else:
                ensure_dir(join(self.test_dir, file))
