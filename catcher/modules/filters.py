import hashlib
import random
import sys
from faker import Faker

from catcher.utils import module_utils
from catcher.utils.singleton import Singleton

random.seed()


def rand_fun(param):
    fake = Faker()
    for modname, importer in module_utils.get_submodules_of('faker.providers'):  # add all known providers
        fake.add_provider(importer.find_module(modname).load_module(modname))
    if hasattr(fake, param):
        return getattr(fake, param)()
    else:
        raise ValueError('Unknown param to randomize: ' + param)


def hash_fun(data, alg='md5'):
    if hasattr(hashlib, alg):
        m = getattr(hashlib, alg)()
        m.update(data.encode())
        return m.hexdigest()
    else:
        raise ValueError('Unknown algorithm: ' + data)


def rand_numeric(range_from=-sys.maxsize - 1, range_to=sys.maxsize):
    return random.randint(range_from, range_to)


def rand_choice(sequence):
    return random.choice(sequence)


class FiltersHolder(metaclass=Singleton):
    def __init__(self, custom_modules=None) -> None:
        super().__init__()
        self.filters = {'hash': hash_fun}
        self.functions = {'random': rand_fun,
                          'random_int': rand_numeric,
                          'random_choice': rand_choice}
        self._import_custom(custom_modules)

    def _import_custom(self, custom_modules):
        """
        Will import all functions started with name 'function_' to global functions and all functions started with
        name 'filter_' to filters. They will be available in templates.
        'function_' and 'filter_' prefixes will be removed from function names during the import.
        :param custom_modules: list of paths to python files where filters of functions are defined.
        """
        if custom_modules:
            for filter_module in custom_modules:
                funs = module_utils.get_all_functions(filter_module)
                for fun_name, fun in funs.items():
                    if fun_name.startswith('function'):
                        import_name = '_'.join(fun_name.split('_')[1:])
                        self.functions[import_name] = fun
                    elif fun_name.startswith('filter'):
                        import_name = '_'.join(fun_name.split('_')[1:])
                        self.filters[import_name] = fun
