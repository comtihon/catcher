from os.path import join

from catcher.utils.module_utils import load_external_actions

TEST_DIR = 'test/tmp'

load_external_actions('catcher.steps')


def get_test_dir(testcase: str) -> str:
    return join(TEST_DIR, testcase)
