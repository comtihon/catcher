Custom filters and functions
============================

Both functions & filters are a piece of python code, which catcher can run from the template. The algorithm is simple:

1. You create a python file with functions you'd like to run from your tests
2. You point catcher to this file (or files)
3. You use it in your templates
4. Profit.

You can use built-in functions and filters implementation :meth:`catcher.modules.filter_impl.bifs` as an example.

Functions
---------

| Catcher support custom functions to be used in templates.
| **Important**: In order to use your function you should **name** it starting with `function_`.
| For example **function_my_fun** will be imported in catcher and can be used as **my_fun** in templates.
| If function doesn't start with `function_` it will be ignored. Although your template's `function_my_fun` can still
 use ignored function itself.
| You can have multiple functions in the same python file.

Imagine you have a file `/home/user/tests/my_functions.py` with content::

    def function_my_custom():
       return {'key': 'value'}

    def some_other_function(arg):
        return 'converted_to_string: ' + str(arg)

In this case `function_my_custom` will be imported and you will be able to use `my_custom` as a function in tests::

    ---
    steps:
        - kafka:
            produce:
                server: '{{ my_kafka }}'
                topic: 'my_topic'
                data: '{{ my_custom() }}'

| To make it work you need to tell catcher where your implementation is. Just run it with `-f` param:
| `catcher -f /home/user/tests/my_functions.py tests/my_test.yml`
| You can have multiple params in case you have multiple modules to import: `-f <module_1> -f <module_2>`

Filters
-------

| You can use filters exactly the same way as functions. Please see Jinja2 `documentation <https://jinja.palletsprojects.com/en/2.11.x/templates/#filters>`_ on what filter is.
| **Important**: In order to use your filter you should **name** it starting with `filter_`.
| For example: **filter_my_filter** will be imported in catcher and can be used as **my_filter** in templates.
| If function doesn't start with `filter_` it will be ignored.
| You can have both functions and filters in the same python file.

Just add this code to `my_functions`, so it should look like this::

    def function_my_custom():
       return {'key': 'value'}

    def filter_increment(input):
       if isinstance(input, int):
         return input + 1
       return 'not an int'

    def some_other_function(arg):
        return 'converted_to_string: ' + str(arg)

In this case you have both `my_custom` function and `increment` filter available for catcher. Let's try the filter::

    ---
    steps:
        - postgres:
            request:
                conf: '{{ postgres }}'
                sql: 'select count(*) from test'
            register: {documents: '{{ OUTPUT.count }}'}
        - kafka:
            produce:
                server: '{{ my_kafka }}'
                topic: 'my_topic'
                data: '{{ documents | increment }}'

You can also have filter with parameters::

    def filter_encode(input, arg='base64'):
        if arg == 'base64':
            import base64
            return base64.b64encode(input.encode()).decode()
        return str(input)

And call it in test with or without param::

    ---
    steps:
        - mongo:
            request:
                conf: '{{ mongo }}'
                collection: 'test'
                insert_one:
                    'user': '{{ username }}'
                    'password_urlencoded': '{{ password | encode('base64') }}'
                    'password_clean': '{{ password | encode }}'

System functions
----------------
| If your python module is already installed in the system (and is available via pydoc.locate) - you can just specify it's
| module path.
| F.e. `my_package/my_module.py`.
| If it is not installed in the system - specify it as a source file: `catcher -f /full/path/to/my_package/my_module.py`.
| If it was already installed in the system - specify only python path: `catcher -f my_package.my_module` **without** py.