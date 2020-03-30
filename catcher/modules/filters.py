from catcher.utils import module_utils
from catcher.utils.singleton import Singleton


class FiltersHolder(metaclass=Singleton):
    def __init__(self, custom_modules=None) -> None:
        super().__init__()
        self.filters = {}
        self.functions = {}
        if not custom_modules:
            custom_modules = []
        custom_modules.append('catcher.modules.filter_impl.bifs')
        self._import_custom(custom_modules)

    def _import_custom(self, custom_modules):
        """
        Will import all functions started with name 'function_' to global functions and all functions started with
        name 'filter_' to filters. They will be available in templates.
        'function_' and 'filter_' prefixes will be removed from function names during the import.
        :param custom_modules: list of paths to python files where filters of functions are defined.
        """
        for filter_module in custom_modules:
            funs = module_utils.get_all_functions(filter_module)
            for fun_name, fun in funs.items():
                if fun_name.startswith('function'):
                    import_name = '_'.join(fun_name.split('_')[1:])
                    self.functions[import_name] = fun
                elif fun_name.startswith('filter'):
                    import_name = '_'.join(fun_name.split('_')[1:])
                    self.filters[import_name] = fun
