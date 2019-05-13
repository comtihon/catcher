import importlib
import ntpath
import os
import pkgutil
from importlib import machinery
from os.path import join
from pydoc import locate
from types import ModuleType

from catcher.utils.logger import warning, error


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


def load_external_actions(package: str):
    """
    Load all classes from a package
    """
    if package.endswith('.py'):
        __load_python_package_by_path(package)
    else:
        __load_python_package_installed(package)


def get_all_subclasses_of(clazz) -> list:
    return clazz.__subclasses__() + [g for s in clazz.__subclasses__()
                                     for g in get_all_subclasses_of(s)]


def is_package_installed(package: str) -> bool:
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False


def __load_python_package_by_path(path: str):
    name = ntpath.basename(path)
    loader = importlib.machinery.SourceFileLoader(name, path)
    mod = ModuleType(loader.name)
    loader.exec_module(mod)


def __load_python_package_installed(package: str):
    modules = locate(package)
    if modules is None:
        return  # package not installed
    for importer, modname, ispkg in pkgutil.walk_packages(path=modules.__path__,
                                                          prefix=modules.__name__ + '.',
                                                          onerror=lambda x: None):
        importlib.import_module(modname)
