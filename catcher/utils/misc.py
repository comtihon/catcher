import ast
import random
import uuid

import time

import datetime
from jinja2 import Template


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def get_all_subclasses_of(clazz) -> list:
    return clazz.__subclasses__() + [g for s in clazz.__subclasses__()
                                     for g in get_all_subclasses_of(s)]


def try_get_object(source: str or dict):
    if isinstance(source, str):
        try:
            source = ast.literal_eval(source)
        except (ValueError, SyntaxError):
            return source
    return source


def fill_template(source: any, variables: dict) -> any:
    if isinstance(source, str):
        source = Template(source).render(inject_builtins(variables))
        try:
            source = ast.literal_eval(source)
        except (ValueError, SyntaxError):
            return source
    return source


def fill_template_str(source: any, variables: dict) -> str:
    return Template(str(source)).render(inject_builtins(variables))


def inject_builtins(variables: dict) -> dict:
    variables_copy = dict(variables)
    variables_copy['RANDOM_STR'] = str(uuid.uuid4())
    variables_copy['RANDOM_INT'] = random.randint(-2147483648, 2147483648)
    ts = time.time()
    variables_copy['NOW_TS'] = ts
    variables_copy['NOW_DT'] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return variables_copy