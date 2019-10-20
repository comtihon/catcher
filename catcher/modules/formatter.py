import time
from abc import ABC, abstractmethod
from os.path import join
from typing import Union


class Formatter(ABC):
    """
    Formatter process logs in log storage and saves it in the desired output
    """

    @abstractmethod
    def format(self, path: str, data: list):
        pass


class JsonFormatter(Formatter):
    def format(self, path: str, data: list):
        import json
        with open(join(path, 'report_' + str(time.time()) + '.json'), 'w') as fp:
            json.dump(data, fp)


class HTMLFormatter(Formatter):
    def format(self, path: str, data: list):
        pass


class OutputFormatter(Formatter):
    def format(self, path: str, data: list):
        print(data)


def formatter_factory(out_format: str) -> Union[Formatter, None]:
    out_format = out_format.lower()
    if out_format == 'json':
        return JsonFormatter()
    elif out_format == 'html':
        return HTMLFormatter()
    else:
        return OutputFormatter()
