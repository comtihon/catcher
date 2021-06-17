import os
import unittest
from os.path import join
from shutil import copyfile

import test
from catcher.modules.log_storage import EmptyLogStorage
from catcher.utils import logger
from catcher.utils.file_utils import ensure_empty, remove_dir, ensure_dir
from catcher.utils.singleton import Singleton
from test import resources


class TestClass(unittest.TestCase):
    def __init__(self, test_name, method_name):
        super().__init__(method_name)
        self._test_name = test_name
        self._test_dir = test.get_test_dir(test_name)
        logger.configure('debug')
        logger.log_storage = EmptyLogStorage('empty')

    @property
    def test_name(self):
        return self._test_name

    @property
    def test_dir(self):
        return join(os.getcwd(), self._test_dir)

    @property
    def test_resources(self):  # test's resource dir (unique per testcase)
        return join(test.get_test_dir(self.test_name), 'resources')

    @property
    def global_resource_dir(self):  # global resource dir (part of project)
        return os.path.dirname(resources.__file__)

    def setUp(self):
        Singleton._instances = {}  # clean singleton between tests
        ensure_empty(test.get_test_dir(self.test_name))
        ensure_empty(self.test_resources)

    def tearDown(self):
        remove_dir(test.get_test_dir(self.test_name))

    def populate_file(self, file: str, content: str):
        with open(join(self.test_dir, file), 'w') as f:
            f.write(content)

    def populate_resource(self, file: str, content: str):
        filename = join(self.test_resources, file)
        ensure_dir(os.path.dirname(os.path.abspath(filename)))
        with open(filename, 'w') as f:
            f.write(content)

    def copy_resource(self, resource_name):
        """
        Copy resource from global resource to the resource dir
        """
        copyfile(join(self.global_resource_dir, resource_name), join(self.test_resources, resource_name))
