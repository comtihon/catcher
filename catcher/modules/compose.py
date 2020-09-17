from os.path import isfile, join

from catcher.modules import Module
from catcher.utils.logger import info
from catcher.utils.module_utils import is_package_installed


class DockerCompose(Module):
    """
    :Docker-compose module:

    Will automatically run `docker-compose up -d` before your test and `down` after it if this
    module was enabled and you have `docker-compose.yml` file in your directory.

    :Enable this module:

    - run `pip install catcher[compose]`. It will installs all requirements, if they were not installed.

    """
    def __init__(self, resources_dir) -> None:
        super().__init__(resources_dir)
        self._cmd = None
        self._options = {'--detach': True,
                         'SERVICE': "",
                         '--no-deps': False,
                         '--abort-on-container-exit': False,
                         '--no-recreate': True,
                         '--remove-orphans': False,
                         '--always-recreate-deps': False,
                         '--force-recreate': False,
                         '--build': False,
                         '--no-build': False,
                         '--no-color': False,
                         '--rmi': 'none',
                         '--volumes': "",
                         '--follow': False,
                         '--timestamps': False,
                         '--scale': {}
                         }

    def before(self, *args, **kwargs):
        """
        Will run `docker-compose up -d` only in case docker-compose is installed locally
        and there is a docker-compose.yml file in resources directory
        """
        compose = self.find_resource_file()
        if compose and is_package_installed('compose'):
            from compose.cli.main import TopLevelCommand, project_from_options
            info('Starting docker-compose. Please wait.')
            self._options['-f'] = join(self._resources, compose),
            self._cmd = TopLevelCommand(project_from_options(self._resources, self._options))
            self._cmd.up(self._options)

    def after(self, *args, **kwargs):
        if self._cmd:
            self._cmd.down(self._options)

    def filter_resource(self, file: str) -> bool:
        # use only default docker-compose.yml for now, will change it in future if needed.
        return isfile(join(self._resources, file)) and file == 'docker-compose.yml'
