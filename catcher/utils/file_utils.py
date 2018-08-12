import inspect
import io
import json
import ntpath
import os
import shutil
from os.path import join

import yaml

from catcher.utils.logger import error


def get_module_filename(module) -> str:
    return ntpath.basename(inspect.getfile(module))[:-3]


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
            if os.path.isfile(path_in_dir) and (path_in_dir.endswith('yaml') or path_in_dir.endswith('yml')):
                file.append(path_in_dir)
            elif os.path.isdir(path_in_dir):
                file += get_files(path_in_dir)
    else:
        file.append(path)
    return file


def read_source_file(file: str) -> dict:
    if not os.path.exists(file):
        err = 'No such file: ' + file
        error(err)
        raise FileNotFoundError(err)
    if file.lower().endswith('json'):
        return _read_json_file(file)
    else:
        return _read_yaml_file(file)


def read_file(file: str) -> str:
    if not os.path.exists(file):
        err = 'No such file: ' + file
        error(err)
        raise FileNotFoundError(err)
    with io.open(file, mode='r', encoding='utf-8') as stream:
        return stream.read()


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


def _read_yaml_file(file: str) -> dict:
    with open(file, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            err = 'Wrong YAML format for file ' + file + ' : ' + str(exc)
            error(err)
            raise yaml.YAMLError(err)


def _read_json_file(file: str) -> dict:
    with open(file, 'r') as stream:
        try:
            return json.load(stream)
        except yaml.YAMLError as exc:
            err = 'Wrong YAML format for file ' + file + ' : ' + str(exc)
            error(err)
            raise yaml.YAMLError(err)
