import json
from copy import deepcopy
from datetime import datetime
from catcher.modules.formatter import formatter_factory
from catcher.utils import file_utils


class LogStorage:
    def __init__(self, output_format) -> None:
        self._data = []
        self._current_test = None
        self._format = output_format
        self.nesting_counter = 0

    def test_start(self, test: str, test_type='test'):
        self._current_test = {'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'file': test,
                              'type': test_type, 'output': [], 'status': 'running'}

    def test_end(self, test, success: bool, output: str = None, test_type='test', end_comment=None):
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
        self._current_test['comment'] = end_comment
        self._data += [{**{'end_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, **self._current_test}]
        self._current_test = None

    def test_parse_fail(self, test: str, output: str):
        self._data += [{'end_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'file': test,
                        'comment': None,
                        'type': 'test',
                        'output': output,
                        'status': 'FAIL'}]

    def nested_test_in(self):
        """
        If test is run from include
        """
        self.nesting_counter += 1

    def nested_test_out(self):
        """
        If test is run from include
        """
        self.nesting_counter -= 1

    def new_step(self, step, variables):
        self._current_test['output'] += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                          'step': self.clean_step_def(step),
                                          'variables': self.clean_vars(variables),
                                          'nested': self.nesting_counter}]

    def step_end(self, step, variables, output: str = None, success: bool = True):
        self._current_test['output'] += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                          'step': self.clean_step_def(step),
                                          'variables': self.clean_vars(variables),
                                          'nested': self.nesting_counter,
                                          'success': success,
                                          'output': output}]

    def output(self, level, output):
        if self._current_test:
            self._current_test['output'] += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                              'data': output,
                                              'level': level}]
        else:
            self._data += [{'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'data': output, 'level': level}]

    def write_report(self, path):
        file_utils.ensure_dir(path)
        formatter = formatter_factory(self._format)
        formatter.format(path, self._data)

    def print_summary(self, path):
        from catcher.utils import logger
        tests = [t for t in self._data if t.get('type') == 'test']
        out_string = self.calculate_statistics(tests)
        for test in tests:
            out_string += '\nTest {}: '.format(file_utils.cut_path(path, test['file']))
            # select only step's ends, which belongs to the current test (excluding registered includes run)
            step_finish_only = [o for o in test['output'] if 'success' in o and o['nested'] == 0]
            if test['status'] == 'OK' and test['comment'] != 'Skipped':
                out_string += logger.green('pass')
            elif test['comment'] == 'Skipped':
                out_string += logger.yellow('skipped')
            else:
                out_string += logger.red('fail') + ', on step {}'.format(len(step_finish_only))
        logger.info(out_string)

    @staticmethod
    def calculate_statistics(tests):
        from catcher.utils import logger
        ok = len([t for t in tests if t['status'] == 'OK' and t['comment'] != 'Skipped'])
        skipped = len([t for t in tests if t['comment'] == 'Skipped'])
        fail = len(tests) - (ok + skipped)
        percent = (ok + skipped) / len(tests) * 100 if len(tests) > 0 else 0
        out_string = 'Test run {}.'.format(logger.blue(str(len(tests))))
        out_string += ' Success: ' + logger.green(str(ok)) + ', Fail: '
        if fail > 0:
            out_string += logger.red(str(fail))
        else:
            out_string += logger.green(str(fail))
        if skipped:
            out_string += ', Skipped: ' + logger.yellow(str(skipped))
        out_string += '. Total: '
        fun = logger.red
        if percent >= 100:
            fun = logger.green
        elif percent >= 66:
            fun = logger.light_green
        elif percent >= 33:
            fun = logger.yellow
        out_string += fun('{:.0f}%'.format(percent))
        return out_string

    def clean_step_def(self, data: dict):
        """ Keep only step definition """
        [step_name] = data.keys()
        step = data[step_name]
        if isinstance(step, str):  # simple step like {'echo': 'hello'}
            return data
        step_def = self.clean_not_renderable_recursive(step)
        return {step_name: step_def}

    def clean_not_renderable_recursive(self, data):
        if not hasattr(data, 'copy'):  # list with primitives [1, 2, 3] should be ignored
            return data
        step_def = data.copy()
        for k, v in data.items():
            if isinstance(v, dict):
                step_def[k] = self.clean_not_renderable_recursive(v)
            elif isinstance(v, list):
                step_def[k] = [self.clean_not_renderable_recursive(t) for t in v]
            elif not self.is_jsonable(v):
                del step_def[k]
        return step_def

    @staticmethod
    def clean_vars(variables: dict):
        """ Clean _get_action(s) non-json serializable functions """
        return deepcopy({k: v for k, v in variables.items() if not callable(v)})

    @staticmethod
    def is_jsonable(x):
        try:
            json.dumps(x)
            return True
        except (TypeError, OverflowError):
            return False


class EmptyLogStorage(LogStorage):
    """
    The default implementation. Does nothing.
    """

    def new_step(self, step, variables):  # ignore variables to free memory
        super().new_step(step, {})

    def step_end(self, step, variables, output: str = None, success: bool = True):  # ignore variables to free memory
        super().step_end(step, {}, output, success)

    def output(self, level, output):
        pass

    def write_report(self, path):
        pass
