import ast
import datetime
import json
import random
import time
import uuid

from os import environ
from jinja2 import Template, UndefinedError


def merge_two_dicts(x, y):
    if not x:
        return y
    if not y:
        return x
    return {**x, **y}


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
    return merge_two_dicts(dict(environ), variables_copy)


def render(source: str, variables: dict) -> str:
    try:
        return Template(source).render(variables)
    except UndefinedError:
        return source
