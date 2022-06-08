import datetime
import os
import time
from abc import ABC, abstractmethod
from os.path import join
from typing import Union

import catcher
from catcher.utils.internal_utils import modify_resource, ensure_resource
from catcher.utils.file_utils import ensure_empty


class Formatter(ABC):
    """
    Formatter process logs in log storage and saves it in the desired output
    """

    @abstractmethod
    def format(self, path: str, reports: str, data: list):
        pass


class JsonFormatter(Formatter):
    def format(self, path: str, reports: str, data: list):
        import json
        with open(join(path, reports, 'report_' + str(time.time()) + '.json'), 'w') as fp:
            json.dump(data, fp)


class HTMLFormatter(Formatter):
    def format(self, path: str, reports: str, data: list):
        self._write_static(join(path, reports))
        total_time = 0
        passed = 0
        failed = 0
        run_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        run_time_dir = join(path, reports, 'run_' + run_time)
        ensure_empty(run_time_dir)
        for test in data:
            test_name = '.'.join(os.path.basename(test['file']).split('.')[:-1]) + '.html'
            test_time = time.mktime(time.strptime(test['end_time'], "%Y-%m-%d %H:%M:%S")) - time.mktime(
                time.strptime(test['start_time'], "%Y-%m-%d %H:%M:%S"))
            if test['status'] == 'OK':
                passed += 1
            else:
                failed += 1
            test['test_time'] = test_time
            total_time += test_time
            test['log_file'] = join(run_time_dir, test_name)
            self._write_test(run_time_dir, test, test_name)
        modify_resource('index.html',
                        dict(test_runs=data, path=path, total_time=total_time, passed=passed, failed=failed),
                        path=join(path, reports, 'index.html'))

    def _write_test(self, path, test, test_name):
        # TODO include and finally.
        raw_log_filename = self._dump_raw_log(path, test, test_name)
        step_finish_only = [o for o in test['output'] if 'success' in o and o['nested'] == 0]
        passed = 0
        failed = 0
        for step in step_finish_only:
            if 'success' in step and step['nested'] == 0:
                step['name'] = list(step['step'].keys())[0]
                if step['success']:
                    passed += 1
                else:
                    if 'output' in step and step['output'] not in [None, '']:
                        step['comment'] = step['output']
                    failed += 1
        modify_resource('test.log.html',
                        dict(steps=step_finish_only,
                             path=path,
                             test_name=test_name,
                             raw_log=raw_log_filename,
                             catcher_v=catcher.APPVSN,
                             result=test['status'] == 'OK',
                             total_time=test['test_time'],
                             passed=passed,
                             failed=failed),
                        path=join(path, test_name))

    @classmethod
    def _write_static(cls, path):
        ensure_resource('logo_small.png', path=path)
        ensure_resource('default.css', path=path)
        ensure_resource('jquery.js', path=path)
        ensure_resource('jquery.expander.min.js', path=path)
        ensure_resource('custom_expand.js', path=path)

    @classmethod
    def _dump_raw_log(cls, path, test, test_name):
        data = []
        for step in test['output']:
            entity = {}
            if 'step' in step:
                if 'success' in step:  # end of step
                    entity['name'] = list(step['step'].keys())[0]
                    entity['body'] = step['step'][entity['name']]
                    entity['variables'] = step['variables']
                    entity['success'] = step['success']
                    entity['output'] = step['output']
                    entity['time'] = step['time']
                    data += [entity]
                continue
            elif 'data' in step:  # log
                entity['name'] = step['level']
                entity['body'] = step['data']
            else:  # unknown output
                entity['name'] = 'unknown'
                entity['body'] = 'unknown'
            entity['time'] = step['time']
            entity['output'] = step.get('output')
            data += [entity]
        raw_log_filename = join(path, '.'.join(os.path.basename(test['file']).split('.')[:-1]) + '.raw.html')
        modify_resource('raw.log.html',
                        dict(logs=data,
                             path=path,
                             test_name=test_name,
                             catcher_v=catcher.APPVSN),
                        path=raw_log_filename)
        return raw_log_filename

    def _dump_system_log(self):
        # TODO
        pass


class OutputFormatter(Formatter):
    def format(self, path: str, reports: str, data: list):
        print(data)


def formatter_factory(out_format: str) -> Union[Formatter, None]:
    out_format = out_format.lower()
    if out_format == 'json':
        return JsonFormatter()
    elif out_format == 'html':
        return HTMLFormatter()
    else:
        return OutputFormatter()
