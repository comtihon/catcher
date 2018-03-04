from catcher.core.test import Test


class Include:
    def __init__(self, **keywords) -> None:
        if 'file' not in keywords:
            raise RuntimeError('Can\'t include unknown file.')
        self._file = keywords['file']
        self._variables = keywords.get('variables', {})
        self._alias = keywords.get('as', None)
        self._run_on_include = keywords.get('run_on_include', self.alias is None)
        self._ignore_errors = keywords.get('ignore_errors', False)
        self._test = None

    @property
    def run_on_include(self) -> bool:
        return self._run_on_include

    @property
    def file(self) -> str:
        return self._file

    @property
    def variables(self) -> dict:
        return self._variables

    @property
    def alias(self) -> str or None:
        return self._alias

    @property
    def ignore_errors(self) -> bool:
        return self._ignore_errors

    @property
    def test(self) -> Test:
        return self._test

    @test.setter
    def test(self, test):
        self._test = test
