import os
import shutil
from os.path import join

import yaml

from catcher.utils.logger import error


# Get list of yaml files in dir and subdirs
def get_files(path: str) -> list:
    if not os.path.exists(path):
        err = 'No such path: ' + path
        error(err)
        raise FileNotFoundError(err)
    file = []
    if os.path.isdir(path):
        for f in os.listdir(path):
            path_in_dir = join(path, f)
            if os.path.isfile(path_in_dir) and path_in_dir.endswith('yaml'):
                file.append(path_in_dir)
            elif os.path.isdir(path_in_dir):
                file += get_files(path_in_dir)
    else:
        file.append(path)
    return file


def read_yaml_file(file: str) -> dict or None:
    if not os.path.exists(file):
        err = 'No such file: ' + file
        error(err)
        raise FileNotFoundError(err)
    with open(file, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            err = 'Wrong YAML format for file ' + file + ' : ' + str(exc)
            error(err)
            raise yaml.YAMLError(err)


# If dir exists delete and and create again
def ensure_empty(path: str):
    remove_dir(path)
    ensure_dir(path)


def remove_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
