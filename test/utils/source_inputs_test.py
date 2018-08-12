import json
from os.path import join

import yaml

from catcher.core.runner import Runner
from test.abs_test_class import TestClass


class InputsTest(TestClass):
    def __init__(self, method_name):
        super().__init__('inputs_test', method_name)

    @property
    def inventory(self) -> dict:
        return {'list': ['a', 'b', 'c']}

    @property
    def test(self) -> dict:
        return {
            'variables': {'dict': {'a': 1, 'b': 2, 'c': 3}},
            'steps': [
                {'check': {'contains': {'the': 'a', 'in': '{{ list }}'}}},
                {'check': {'contains': {'the': 'a', 'in': '{{ dict }}'}}}
            ]
        }

    def test_yaml_lowercase(self):
        with open(join(self.test_dir, 'inventory.yaml'), 'w') as outfile:
            yaml.dump(self.inventory, outfile)
        with open(join(self.test_dir, 'main.yaml'), 'w') as outfile:
            yaml.dump(self.test, outfile)
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yaml'), join(self.test_dir, 'inventory.yaml'))
        self.assertTrue(runner.run_tests())

    def test_yaml_uppercase(self):
        with open(join(self.test_dir, 'inventory.YAML'), 'w') as outfile:
            yaml.dump(self.inventory, outfile)
        with open(join(self.test_dir, 'main.YAML'), 'w') as outfile:
            yaml.dump(self.test, outfile)
        runner = Runner(self.test_dir, join(self.test_dir, 'main.YAML'), join(self.test_dir, 'inventory.YAML'))
        self.assertTrue(runner.run_tests())

    def test_yml_lowercase(self):
        with open(join(self.test_dir, 'inventory.yml'), 'w') as outfile:
            yaml.dump(self.inventory, outfile)
        with open(join(self.test_dir, 'main.yml'), 'w') as outfile:
            yaml.dump(self.test, outfile)
        runner = Runner(self.test_dir, join(self.test_dir, 'main.yml'), join(self.test_dir, 'inventory.yml'))
        self.assertTrue(runner.run_tests())

    def test_yml_uppercase(self):
        with open(join(self.test_dir, 'inventory.YML'), 'w') as outfile:
            yaml.dump(self.inventory, outfile)
        with open(join(self.test_dir, 'main.YML'), 'w') as outfile:
            yaml.dump(self.test, outfile)
        runner = Runner(self.test_dir, join(self.test_dir, 'main.YML'), join(self.test_dir, 'inventory.YML'))
        self.assertTrue(runner.run_tests())

    def test_json_lowercase(self):
        with open(join(self.test_dir, 'inventory.json'), 'w') as outfile:
            json.dump(self.inventory, outfile)
        with open(join(self.test_dir, 'main.json'), 'w') as outfile:
            json.dump(self.test, outfile)
        runner = Runner(self.test_dir, join(self.test_dir, 'main.json'), join(self.test_dir, 'inventory.json'))
        self.assertTrue(runner.run_tests())

    def test_json_uppercase(self):
        with open(join(self.test_dir, 'inventory.JSON'), 'w') as outfile:
            json.dump(self.inventory, outfile)
        with open(join(self.test_dir, 'main.JSON'), 'w') as outfile:
            json.dump(self.test, outfile)
        runner = Runner(self.test_dir, join(self.test_dir, 'main.JSON'), join(self.test_dir, 'inventory.JSON'))
        self.assertTrue(runner.run_tests())
