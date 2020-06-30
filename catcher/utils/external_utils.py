import json
import os
import subprocess
from typing import Union, List, Optional, Tuple

from catcher.utils.logger import warning, debug
from catcher.utils import file_utils

from json import JSONDecodeError


def run_cmd(cmd: Union[List[str], str], variables, cwd=None, shell=False):
    env = _prepare_env(variables)
    process = subprocess.Popen(cmd,
                               cwd=cwd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,
                               env=env,
                               shell=shell)
    stdout, stderr = process.communicate()
    return process.returncode, _parse_output(stdout), stderr


def run_cmd_simple(cmd: str,
                   variables: dict,
                   env=None,
                   args: List[str] = None) -> Union[dict, str]:
    """
    Run cmd with variables written in environment.
    :param args: cmd arguments
    :param cmd: to run
    :param variables: variables
    :param env: custom environment
    :return: output in json (if can be parsed) or plaintext
    """
    env = _prepare_env(variables, env=env)
    cmd, cwd = _prepare_cmd(cmd, args, variables)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, cwd=cwd)
    if p.wait() == 0:
        out = p.stdout.read().decode()
        debug(out)
        return _parse_output(out)
    else:
        out = p.stdout.read().decode()
        warning(out)
        raise Exception('Execution failed.')


def _prepare_env(variables, env=None):
    if env is None:
        env = os.environ.copy()
    for k, v in variables.items():
        env[k] = str(v)
    return env


def _prepare_cmd(file: str, args: list = None, variables=None) -> Tuple[List[str], Optional[str]]:
    cmd = None
    cwd = None
    if file.endswith('.py'):  # python executable
        cmd = ['python', file]
    if file.endswith('.js'):  # node js executable
        cmd = ['node', file]
    # TODO Scala compilation?
    if file.endswith('.java'):  # java source file (need to compile)
        cmd = ['java', _compile_java(file, variables)]
        cwd = variables['RESOURCES_DIR']  # compiled java class should be run from resources
    if file.endswith('.kt'):  # kotlin source file (need to compile)
        cmd = ['java', '-jar', _compile_kotlin(file, variables)]
        cwd = variables['RESOURCES_DIR']  # compiled java class should be run from resources
    if file.endswith('.jar'):  # executable jar
        cmd = ['java', '-jar', file]
    if cmd is None:  # local executable or other command
        cmd = [file]
    if args is not None:
        cmd += args
    debug(str(cmd))
    return cmd, cwd


def _compile_java(file, variables):
    resource_dir = variables['RESOURCES_DIR']
    return_code, stdout, stderr = run_cmd('javac -d . *.java',
                                          variables,
                                          cwd=resource_dir,
                                          shell=True)  # compile everything
    if return_code != 0:
        raise Exception("Can't compile {}. Out: {}, Err: {}".format(file, stdout, stderr))
    class_file = file_utils.find_resource(resource_dir, file_utils.get_filename(file), '.class')
    module = file_utils.cut_part_path(resource_dir, class_file).replace('/', '.')
    return module.split('.class')[0]


def _compile_kotlin(file, variables):
    resource_dir = variables['RESOURCES_DIR']
    filename = file_utils.get_filename(file)
    return_code, stdout, stderr = run_cmd('kotlinc {}.kt -include-runtime -d {}.jar'.format(filename, filename),
                                          variables,
                                          cwd=resource_dir,
                                          shell=True)  # compile everything
    if return_code != 0:
        raise Exception("Can't compile {}. Out: {}, Err: {}".format(file, stdout, stderr))
    return filename + '.jar'


def _parse_output(output: str):
    try:
        return json.loads(output)
    except JSONDecodeError:
        return output
