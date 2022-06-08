import datetime
import os
import sys
import inspect
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
    def format(self, path: str, reports: str, data: list, steps, modules, bifs):
        pass


class JsonFormatter(Formatter):
    def format(self, path: str, reports: str, data: list, steps, modules, bifs):
        import json
        with open(join(path, reports, 'report_' + str(time.time()) + '.json'), 'w') as fp:
            json.dump(data, fp)


class HTMLFormatter(Formatter):
    def format(self, path: str, reports: str, data: list, steps, modules, bifs):
        self._dump_system_log(join(path, reports), steps, modules, bifs)
        self._write_static(join(path, reports))
        total_time = 0
        passed = 0
        failed = 0
        run_time_dir = join(path, reports, 'run_' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        ensure_empty(run_time_dir)
        tests = self._form_tests(run_time_dir, data)
        for test in tests:
            if test['status'] == 'OK':
                passed += 1
            else:
                failed += 1
            if test['status'] == 'CRASH':
                failed += 1
                continue
            test_time = time.mktime(time.strptime(test['end_time'], "%Y-%m-%d %H:%M:%S")) - time.mktime(
                time.strptime(test['start_time'], "%Y-%m-%d %H:%M:%S"))
            test['test_time'] = test_time
            test['filepath'] = join(path, test['file'])
            total_time += test_time
            self._write_test(run_time_dir, test)
        modify_resource('index.html',
                        dict(test_runs=tests,
                             total_time=total_time,
                             catcher_v=catcher.APPVSN,
                             passed=passed,
                             failed=failed),
                        path=join(path, reports, 'index.html'))

    @classmethod
    def _form_tests(cls, run_time_dir: str, data: list):
        test_runs = []
        last_added = None
        for test in data:
            try:
                if test['type'] in ['test', 'include']:
                    test_name = '.'.join(os.path.basename(test['file']).split('.')[:-1]) + '.html'
                    test['name'] = test_name
                    test['log_file'] = join(run_time_dir, test_name)
                    test_runs += [test]
                    last_added = test
                elif test['type'].endswith('_cleanup'):  # add cleanup to the last added test as cleanup
                    last_added['end_time'] = test['end_time']
                    for step in test['output']:
                        if 'comment' in step:
                            step['comment'] = 'Cleanup; ' + step['comment']
                        else:
                            step['comment'] = 'Cleanup.'
                        last_added['output'] += [step]
            except KeyError:
                test['status'] = 'CRASH'
                test_runs += [test]
        return test_runs

    def _write_test(self, path, test):
        raw_log_filename = self._dump_raw_log(path, test, test['name'])
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
                             test_name=test['name'],
                             raw_log=raw_log_filename,
                             catcher_v=catcher.APPVSN,
                             result=test['status'] == 'OK',
                             total_time=test['test_time'],
                             passed=passed,
                             failed=failed),
                        path=join(path, test['name']))

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
        if isinstance(test['output'], str):  # no such file error
            return None
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

    @classmethod
    def _dump_system_log(cls, path: str, steps: dict, modules: dict, bifs):
        modify_resource('system.log.html',
                        dict(steps=[{'name': k, 'file': inspect.getfile(v)} for k, v in steps.items()],
                             modules=[{'name': k, 'file': inspect.getfile(v.__class__)} for k, v in modules.items()],
                             filters=[{'name': k, 'file': inspect.getfile(v)} for k, v in bifs._filters.items()],
                             functions=[{'name': k, 'file': inspect.getfile(v)} for k, v in bifs._functions.items()],
                             catcher_v=catcher.APPVSN,
                             py_v=sys.version),
                        path=join(path, 'system.log.html'))


class OutputFormatter(Formatter):
    def format(self, path: str, reports: str, data: list, steps, modules, bifs):
        print(data)


def formatter_factory(out_format: str) -> Union[Formatter, None]:
    out_format = out_format.lower()
    if out_format == 'json':
        return JsonFormatter()
    elif out_format == 'html':
        return HTMLFormatter()
    else:
        return OutputFormatter()
