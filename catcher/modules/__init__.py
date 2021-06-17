from abc import ABC, abstractmethod
from os import listdir
from os.path import join
from typing import Union


class Module(ABC):

    def __init__(self, resources) -> None:
        super().__init__()
        self._resources = resources

    @abstractmethod
    def before(self, *args, **kwargs):
        """
        Run before tests execution
        """
        pass

    @abstractmethod
    def after(self, *args, **kwargs):
        """
        Run after tests execution
        """
        pass

    def find_resource_file(self) -> Union[str, None]:
        """ find a file inside a resources directory """
        if self._resources is None:
            return None
        try:
            files = [f for f in listdir(self._resources) if self.filter_resource(f)]
            if files:
                return join(self._resources, files[0])
            return None
        except FileNotFoundError:
            return None

    @abstractmethod
    def filter_resource(self, file: str) -> bool:
        pass
