import importlib
import os
import pkgutil
from os.path import join
from pydoc import locate

from catcher.steps.external_step import ExternalStep
from catcher.utils.file_utils import get_module_filename
from catcher.utils.logger import warning, error


def prepare_modules(module_paths: list) -> dict:
    """
    Scan all paths for external modules and form key-value dict.
    :param module_paths:
    :return: dict of external modules, where keys are filenames (same as stepnames)
     and values are the paths
    """
    indexed = {}
    for path in module_paths:
        if not os.path.exists(path):
            err = 'No such path: ' + path
            error(err)
        else:
            for f in os.listdir(path):
                mod_path = join(path, f)
                if f in indexed:
                    warning('Override ' + indexed[f] + ' with ' + mod_path)
                indexed[f] = mod_path
    return indexed


def get_external_actions() -> dict:
    """
    Scan catcher_modules package for all additional modules (if installed) and form a dict
    where keys are filenames (same as stepnames) and values are classes implementing ExternalStep
    :return: dict of modules implementing ExternalStep from catcher_modules package
    """
    core_modules = locate('catcher-modules')
    if core_modules is None:
        return {}  # catcher-modules not installed
    for importer, modname, ispkg in pkgutil.walk_packages(path=core_modules.__path__,
                                                          prefix=core_modules.__name__ + '.',
                                                          onerror=lambda x: None):
        importlib.import_module(modname)
    external = get_all_subclasses_of(ExternalStep)
    found = {}
    for module in external:
        found[get_module_filename(module)] = module
    return found


def get_all_subclasses_of(clazz) -> list:
    return clazz.__subclasses__() + [g for s in clazz.__subclasses__()
                                     for g in get_all_subclasses_of(s)]
