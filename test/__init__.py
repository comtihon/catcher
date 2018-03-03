from os.path import join

TEST_DIR = 'test/tmp'


def get_test_dir(testcase: str) -> str:
    return join(TEST_DIR, testcase)
