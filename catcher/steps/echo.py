from os.path import join
from catcher.steps.step import Step
from catcher.utils.logger import info
from catcher.utils.misc import fill_template


class Echo(Step):
    def __init__(self, path: str, body: dict) -> None:
        super().__init__(body)
        self._export_from = body['from']
        self._export_to = body.get('to', None)
        self._path = path

    @property
    def source(self) -> str:
        return self._export_from

    @property
    def dst(self) -> str or None:
        return self._export_to

    @property
    def path(self):
        return self._path

    def action(self, includes: dict, variables: dict) -> dict:
        out = fill_template(self.source, variables)
        if self.dst is None:
            info(out)
        else:
            dst = fill_template(self.dst, variables)
            with open(join(self.path, dst), 'w') as f:
                f.write(str(out))
        return self.process_register(variables)
