from catcher.utils.singleton import Singleton
from catcher.modules.compose import DockerCompose
from catcher.modules.requirements import Requirements
from catcher.utils.logger import debug


class ModulesFactory(metaclass=Singleton):

    def __init__(self, **kwargs) -> None:
        """
        :param kwargs: resources_dir param must exist for the initial load
        """
        super().__init__()
        # TODO find all submodules of catcher.modules.Module dynamically!
        self._modules = {'compose': DockerCompose(kwargs['resources_dir']),
                         'requirements': Requirements(kwargs['resources_dir'])}
        debug('Loaded modules: {}'.format(list(self._modules.keys())))

    @property
    def modules(self):
        return self._modules
