import os


def check_file(file: str, expected: str) -> bool:
    if not os.path.exists(file):
        return False
    with open(file, 'r') as f:
        content = f.read()
        if content != expected:
            print('Got ' + content + ' instead of expected ' + expected)
            return False
        return True


def read_file(file: str) -> str:
    with open(file, 'r') as f:
        return f.read()
