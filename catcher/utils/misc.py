import ast

from jinja2 import Template


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def get_all_subclasses_of(clazz) -> list:
    return clazz.__subclasses__() + [g for s in clazz.__subclasses__()
                                     for g in get_all_subclasses_of(s)]


def fill_template(source: any, variables: dict) -> any:
    if isinstance(source, str):
        source = Template(source).render(variables)
        try:
            source = ast.literal_eval(source)
        except (ValueError, SyntaxError):
            return source
    return source
