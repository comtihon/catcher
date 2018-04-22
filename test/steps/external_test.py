import os
import stat
from os.path import join

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class ExternalTest(TestClass):
    def __init__(self, method_name):
        super().__init__('external', method_name)

    def test_run_external(self):
        self.write_module('math', '''#!/bin/bash
        one=$(echo ${1} | jq -r '.add.the')
        two=$(echo ${1} | jq -r '.add.to')
        echo $((${one} + ${two}))
        ''')
        self.populate_file('main.yaml', '''---
        steps:
            - math:
                add: {the: 1, to: 2}
                register: {sum: '{{ OUTPUT }}'}
            - check: {equals: {the: '{{ sum }}', is: 3}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, modules=[self.test_dir])
        self.assertTrue(runner.run_tests())

    def test_run_external_with_vars(self):
        self.write_module('math', '''#!/bin/bash
        one=$(echo ${1} | jq -r '.add.the')
        two=$(echo ${1} | jq -r '.add.to')
        echo $((${one} + ${two}))
        ''')
        self.populate_file('main.yaml', '''---
        variables:
            one: 1
            two: 2
        steps:
            - math:
                add: {the: '{{ one }}', to: '{{ two }}'}
                register: {sum: '{{ OUTPUT }}'}
            - check: {equals: {the: '{{ sum }}', is: 3}}
        ''')
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), None, modules=[self.test_dir])
        self.assertTrue(runner.run_tests())

    def write_module(self, name: str, body: str):
        self.populate_file(name, body)
        path = join(self.test_dir, name)
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)
