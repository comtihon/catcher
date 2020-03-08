from copy import deepcopy
from datetime import datetime
from catcher.modules.formatter import formatter_factory
from catcher.utils import file_utils


class LogStorage:
    def __init__(self, output_format) -> None:
        self._data = []
        self._current_test = None
        self._format = output_format

    def test_start(self, test: str, test_type='test'):
        self._current_test = {'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'file': test,
                              'type': test_type, 'output': [], 'status': 'running'}

    def test_end(self, test, success: bool, output: str = None, test_type='test'):
        if self._current_test:
            if success:
                self._current_test['status'] = 'OK'
            else:
                if output:
                    self._current_test['status'] = output
                else:
                    self._current_test['status'] = 'FAIL'
        else:
            self._current_test = {}  # to avoid NPE on the next line
        self._data += [{**{'end_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, **self._current_test}]
        self._current_test = None

    def new_step(self, step, variables):
        self._current_test['output'] += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                          'step': self.clean_step_def(step), 'variables': self.clean_vars(variables)}]

    def step_end(self, step, variables, output: str = None, success: bool = True):
        self._current_test['output'] += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                          'step': self.clean_step_def(step),
                                          'variables': self.clean_vars(variables), 'success': success, 'output': output}]

    def output(self, level, output):
        if self._current_test:
            self._current_test['output'] += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                              'data': output, 'level': level}]
        else:
            self._data += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'data': output, 'level': level}]

    def write_report(self, path):
        file_utils.ensure_dir(path)
        formatter = formatter_factory(self._format)
        formatter.format(path, self._data)

    @staticmethod
    def clean_step_def(data: dict):
        """ Keep only step definition """
        [step_name] = data.keys()
        step = data[step_name]
        if isinstance(step, str):  # simple step like {'echo': 'hello'}
            return data
        step_def = step.copy()
        for k in step.keys():
            if k.startswith('_'):
                del step_def[k]
        return {step_name: step_def}

    @staticmethod
    def clean_vars(variables: dict):
        """ Clean _get_action(s) non-json serializable functions """
        return deepcopy({k: v for k, v in variables.items() if not callable(v)})


class EmptyLogStorage(LogStorage):
    """
    The default implementation. Does nothing.
    """

    def test_start(self, path, test_type='test'):
        pass

    def test_end(self, test, success: bool, output: str = None, test_type='test'):
        pass

    def new_step(self, step, variables):
        pass

    def step_end(self, step, variables, output: str = None, success: bool = True):
        pass

    def output(self, level, output):
        pass

    def write_report(self, path):
        pass
