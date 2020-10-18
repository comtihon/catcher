import importlib
import importlib.util
import inspect
import os
import pkgutil
import sys
from contextlib import contextmanager
from inspect import getmembers, isfunction
from os.path import join
from pydoc import locate
from types import ModuleType
from typing import Union

from catcher.utils.logger import warning, error, debug


def prepare_modules(module_paths: list, available: dict) -> dict:
    """
    Scan all paths for external modules and form key-value dict.
    :param module_paths: list of external modules (either python packages or third-party scripts)
    :param available: dict of all registered python modules (can contain python modules from module_paths)
    :return: dict of external modules, where keys are filenames (same as stepnames) and values are the paths
    """
    indexed = {}
    for path in module_paths:
        if not os.path.exists(path) and path not in available:
            err = 'No such path: ' + path
            error(err)
        else:
            for f in os.listdir(path):
                mod_path = join(path, f)
                if f in indexed:
                    warning('Override ' + indexed[f] + ' with ' + mod_path)
                indexed[f] = mod_path
    return indexed


def get_submodules_of(package: str):
    """
    Get all submodules and their importers for the package. It is not recursive.
    For recursive see __load_python_package_installed
    Package should be installed in the system.
    """
    modules = locate(package)
    return [(modname, importer) for importer, modname, ispkg
            in pkgutil.iter_modules(path=modules.__path__, prefix=modules.__name__ + '.')]


def load_external_actions(package: str):
    """
    Load all classes from a package
    """
    if package.endswith('.py'):
        return __load_python_package_by_path(package)
    else:
        return __load_python_package_installed(package)


def get_all_subclasses_of(clazz) -> list:
    return clazz.__subclasses__() + [g for s in clazz.__subclasses__()
                                     for g in get_all_subclasses_of(s)]


def is_package_installed(package: str) -> bool:
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False


def add_package_to_globals(package: str, glob=None, warn_missing_package=True) -> dict:
    if glob is None:
        glob = globals()
    try:
        mod = importlib.import_module(package)
        glob[package] = mod
    except ImportError as e:
        if warn_missing_package:
            warning(str(e))
        else:
            debug(str(e))
    return glob


def get_all_functions(module: str) -> dict:
    mod = load_external_actions(module)
    if isinstance(mod, list):
        res = {}
        for m in mod:
            res = {**res, **dict([o for o in getmembers(m) if isfunction(o[1])])}
        return res
    else:
        return dict([o for o in getmembers(mod) if isfunction(o[1])])


def get_all_classes(module: Union[str, ModuleType]) -> dict:
    if isinstance(module, str):
        module = sys.modules[module]
    return dict(inspect.getmembers(module, inspect.isclass))


@contextmanager
def add_to_path(p):
    import sys
    old_path = sys.path
    sys.path = sys.path[:]
    sys.path.insert(0, p)
    try:
        yield
    finally:
        sys.path = old_path


def __load_python_package_by_path(path: str):
    with add_to_path(os.path.dirname(path)):
        spec = importlib.util.spec_from_file_location(path, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def __load_python_package_installed(package: str):
    modules = locate(package)
    if modules is None:
        return  # package not installed
    if not hasattr(modules, '__path__'):
        return modules
    return [importlib.import_module(modname)
            for importer, modname, ispkg in pkgutil.walk_packages(path=modules.__path__,
                                                                  prefix=modules.__name__ + '.',
                                                                  onerror=lambda x: None)]
