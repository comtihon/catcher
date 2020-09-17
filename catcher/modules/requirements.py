import subprocess
import sys
from os.path import isfile, join

from catcher.modules import Module
from catcher.utils.logger import debug


class Requirements(Module):
    """
    :Python requirements module:

    Will automatically install all packages from ``requirements.txt`` before running tests, if
    finds it in the root of the resource directory.

    """

    def __init__(self, resources_dir) -> None:
        super().__init__(resources_dir)

    def before(self, *args, **kwargs):
        requirements = self.find_resource_file()
        if requirements:
            debug('Installing requirements: {}'.format(requirements))
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements])

    def after(self, *args, **kwargs):
        # does nothing
        pass

    def filter_resource(self, file: str) -> bool:
        # use only default docker-compose.yml for now, will change it in future if needed.
        return isfile(join(self._resources, file)) and file == 'requirements.txt'
