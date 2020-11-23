import ast
import datetime
import json
import random
import time
import uuid
from collections.abc import Iterable
from types import ModuleType

from jinja2 import Template, UndefinedError

from catcher.utils import module_utils
from catcher.utils.logger import debug
from catcher.core.filters_factory import FiltersFactory


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


def try_get_objects(source: str or dict or list):
    got = try_get_object(source)  # "'[1,2,3]'" -> '[1,2,3]' -> [1,2,3]
    got = try_get_object(got)  # '[1,2,3]' -> [1,2,3]
    if isinstance(got, dict):
        return dict([(k, try_get_objects(v)) for k, v in got.items()])
    if isinstance(got, list):
        return [try_get_objects(v) for v in got]
    return got


def try_get_object(source: str or dict or list):
    if isinstance(source, str):
        try:  # try python term '{key: "value"}'
            evaled = eval_datetime(source)
            if isinstance(evaled, ModuleType) or callable(evaled):  # for standalone 'string' var or 'id' bif
                return source
            source = evaled
        except Exception:
            try:  # try json object '{"key" : "value"}'
                source = json.loads(source)
            except ValueError:
                return source
    return source


def fill_template(source: any, variables: dict, isjson=False, glob=None, globs_added=None) -> any:
    if not globs_added:
        globs_added = set()
    if isinstance(source, str):
        source = render(source, inject_builtins(variables))
        if isjson:  # do not parse json string back to objects
            return source
        try:
            evaled = format_datetime(eval_datetime(source, glob))
            if not isinstance(evaled, ModuleType) and not callable(evaled):  # for standalone 'string' var or 'id' bif
                source = evaled
        except NameError as e:  # try to import missing package and rerun this code
            if 'is not defined' in str(e):
                name = str(e).split("'")[1]
                if name not in globs_added:
                    # f.e. tzinfo=psycopg2.tz.FixedOffsetTimezone for datetime
                    glob = module_utils.add_package_to_globals(name, glob, warn_missing_package=False)
                    globs_added.add(name)
                    filled = fill_template(source, variables, isjson, glob=glob, globs_added=globs_added)
                    if not isinstance(filled, ModuleType) and not callable(filled):
                        return filled  # for standalone 'string' var or 'id' bif
        except Exception:
            pass
    return source


def fill_template_str(source: any, variables: dict) -> str:
    rendered = render(str(source), inject_builtins(variables))
    if rendered != source:
        return fill_template_str(rendered, variables)
    return rendered


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
            return dict([(format_datetime(k), format_datetime(v)) for k, v in iterable.items()])
        elif isinstance(iterable, tuple):
            return tuple([format_datetime(i) for i in iterable])
        return [format_datetime(i) for i in iterable]


def inject_builtins(variables: dict) -> dict:
    variables_copy = dict(variables)
    variables_copy['RANDOM_STR'] = str(uuid.uuid4())
    variables_copy['RANDOM_INT'] = random.randint(-2147483648, 2147483648)
    ts = round(time.time(), 6)  # from timestamp uses rounding, so we should also use it here, to make them compatible
    variables_copy['NOW_TS'] = ts
    variables_copy['NOW_DT'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S0+0000')
    return variables_copy


def render(source: str, variables: dict) -> str:
    template = Template(source)
    holder = FiltersFactory()
    for filter_mod, value in holder.filters.items():
        template.environment.filters[filter_mod] = value
    for fun_mod, value in holder.functions.items():
        template.globals[fun_mod] = value
    try:
        return template.render(variables)
    except UndefinedError as e:
        debug(e.message)
        return source
