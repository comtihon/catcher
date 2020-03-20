import ast
import datetime
import json
import random
import sys
import time
import uuid
import hashlib
from collections import Iterable
from types import ModuleType

from faker import Faker
from jinja2 import Template, UndefinedError

from catcher.utils import module_utils
from catcher.utils.logger import debug

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
            source = eval_datetime(source)
        except Exception:
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


def fill_template(source: any, variables: dict, isjson=False, glob=None, globs_added=None) -> any:
    if not globs_added:
        globs_added = set()
    if isinstance(source, str):
        source = render(source, inject_builtins(variables))
        if isjson:  # do not parse json string back to objects
            return source
        try:
            source = format_datetime(eval_datetime(source, glob))
        except NameError as e:  # try to import missing package and rerun this code
            if 'is not defined' in str(e):
                name = str(e).split("'")[1]
                if name not in globs_added:
                    # f.e. tzinfo=psycopg2.tz.FixedOffsetTimezone for datetime
                    glob = module_utils.add_package_to_globals(name, glob)
                    globs_added.add(name)
                    filled = fill_template(source, variables, isjson, glob=glob, globs_added=globs_added)
                    if not isinstance(filled, ModuleType):  # for standalone 'string' var
                        return filled
        except Exception:
            pass
    return source


def eval_datetime(astr, glob=None):
    if glob is None:
        glob = globals()
    try:
        tree = ast.parse(astr)
    except SyntaxError:
        raise ValueError(astr)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.Expr, ast.Dict, ast.Str,
                             ast.Attribute, ast.Num, ast.Name, ast.Load, ast.Tuple)): continue
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'datetime'): continue
        pass
    return eval(astr, glob)


def format_datetime(iterable):
    if not isinstance(iterable, Iterable) or isinstance(iterable, str):
        if isinstance(iterable, datetime.datetime):
            return iterable.strftime('%Y-%m-%d %H:%M:%S.%f')
        return iterable
    else:
        if isinstance(iterable, dict):
            return dict([(format_datetime(k), format_datetime(v)) for k, v in iterable.items()])  # TODO ordered dict?
        elif isinstance(iterable, tuple):
            return tuple([format_datetime(i) for i in iterable])
        return [format_datetime(i) for i in iterable]


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
    for modname, importer in module_utils.get_submodules_of('faker.providers'):  # add all known providers
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
    except UndefinedError as e:
        debug(e.message())
        return source
