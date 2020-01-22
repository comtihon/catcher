import ast
import datetime
import json
import random
import sys
import time
import uuid
import hashlib
from faker import Faker
from jinja2 import Template, UndefinedError

from catcher.utils.module_utils import get_submodules_of

random.seed()


def merge_two_dicts(x, y):
    if not x:
        return y
    if not y:
        return x
    return {**x, **y}


def report_override(variables: dict, override: dict):
    existing = set(variables)
    replace = set(override)
    return list(existing.intersection(replace))


def try_get_object(source: str or dict or list):
    if isinstance(source, str):
        try:  # try python term '{key: "value"}'
            source = ast.literal_eval(source)
        except (ValueError, SyntaxError):
            try:  # try json object '{"key" : "value"}'
                source = json.loads(source)
            except ValueError:
                return source
    return source


def try_get_objects(source: str or dict or list):
    got = try_get_object(source)  # "'[1,2,3]'" -> '[1,2,3]' -> [1,2,3]
    got = try_get_object(got)  # '[1,2,3]' -> [1,2,3]
    if isinstance(got, dict):
        return dict([(k, try_get_objects(v)) for k, v in got.items()])
    if isinstance(got, list):
        return [try_get_objects(v) for v in got]
    return got


def fill_template(source: any, variables: dict, isjson=False) -> any:
    if isinstance(source, str):
        source = render(source, inject_builtins(variables))
        if isjson:  # do not parse json string back to objects
            return source
        try:
            source = ast.literal_eval(source)
        except (ValueError, SyntaxError):
            return source
    return source


def fill_template_str(source: any, variables: dict) -> str:
    return render(str(source), inject_builtins(variables))


def inject_builtins(variables: dict) -> dict:
    variables_copy = dict(variables)
    variables_copy['RANDOM_STR'] = str(uuid.uuid4())
    variables_copy['RANDOM_INT'] = random.randint(-2147483648, 2147483648)
    ts = time.time()
    variables_copy['NOW_TS'] = ts
    variables_copy['NOW_DT'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S0+0000')
    return variables_copy


def rand_fun(param):
    fake = Faker()
    for modname, importer in get_submodules_of('faker.providers'):  # add all known providers
        fake.add_provider(importer.find_module(modname).load_module(modname))
    if hasattr(fake, param):
        return getattr(fake, param)()
    else:
        raise ValueError('Unknown param to randomize: ' + param)


def hash_fun(data, alg='md5'):
    if hasattr(hashlib, alg):
        m = getattr(hashlib, alg)()
        m.update(data.encode())
        return m.hexdigest()
    else:
        raise ValueError('Unknown algorithm: ' + data)


def rand_numeric(range_from=-sys.maxsize - 1, range_to=sys.maxsize):
    return random.randint(range_from, range_to)


def rand_choice(sequence):
    return random.choice(sequence)


def render(source: str, variables: dict) -> str:
    template = Template(source)
    template.globals['random'] = rand_fun
    template.globals['random_int'] = rand_numeric
    template.globals['random_choice'] = rand_choice
    template.environment.filters['hash'] = hash_fun
    try:
        return template.render(variables)
    except UndefinedError:
        return source
