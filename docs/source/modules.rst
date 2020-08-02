Custom Modules
==============

| Catcher has a flexible modular system. If built-in modules functionality is not enough you can use your own modules.
| Read :doc:`tests` for more info about running and naming steps, registering and using variables.

Built-in
--------
There are build in modules, shipped with catcher. You can learn about their usage in :doc:`internal_modules`.

Additional
----------
There are additional catcher modules available in this repository: `Catcher-Modules <https://github.com/comtihon/catcher_modules>`_

External
--------

Python module
^^^^^^^^^^^^^
Writing external scripts in Python is a bit easier. All you need is:

1. Inherit from :meth:`catcher.steps.external_step.ExternalStep`
2. Use :meth:`catcher.steps.step.update_variables` annotation on your action method implementation.
3. Your function should return variables (from input) and output (optional). Do not modify variables inside function
   (it is bad practice)
4. Include path/to/your/module to catcher: `catcher -i intentory.yaml test.yaml -m my.python.package`

You can use :meth:`catcher.steps.external_step.ExternalStep.simple_input` to fill all templates.

`hello.py` example::

    from catcher.steps.external_step import ExternalStep
    from catcher.steps.step import update_variables


    class HelloStep(ExternalStep):
        """
        Very important and useful step. Says hello to input. Return as a string.
        Example usage.
        ::
            hello:
                say: 'John Doe'
                register: {greeting='{{ OUTPUT }}'}

        """
        @update_variables
        def action(self, includes: dict, variables: dict) -> (dict, str):
            body = self.simple_input(variables)
            person = body['say']
            return variables, 'hello {}'.format(person)

Other languages - executable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can easily write your own modules and plug them to catcher:

1. write your module (it should be executable)
2. use it in your test script
3. tell catcher where it is

For example you've developed a `math` module::

   #!/bin/bash
   one=$(echo ${1} | jq -r '.add.the')
   two=$(echo ${1} | jq -r '.add.to')
   echo $((${one} + ${two}))

to sum `the` and `to`.
Then in test script you will write::

   ---
   variables:
     one: 1
     two: 2
   steps:
       - math:
           add: {the: '{{ one }}', to: '{{ two }}'}
           register: {sum: '{{ OUTPUT }}'}

| To run it just tell the Catcher where your script is:
| `catcher your_test.yaml -m path/to/your/module`
| Catcher will find your `math` module (by the step name) in `path/to/your/module` directory
  and call it with `{"add": {"the": "1","to": "2"}}` argument. Your file's stdout will be the
  step's `OUTPUT`.

Other languages - compiled/VM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Catcher also supports not-executable (can't be run as `./your_step`) external steps. F.e. java files compiled in a Jar::

    variables:
        person: 'John Doe'
    steps:
        - MyClass.jar:
            say: '{{ person }}'
            register: {greeting: '{{ OUTPUT }}'}
        - check: {equals: {the: '{{ greeting.strip() }}', is: 'hello John Doe'}}

Catcher will run **MyClass.jar** (should be in resources directory) with local **java** (should be installed). In this case
all arguments (like **say** in this example) will be passed as command-line arguments in JSON format (argv in main function on Java-side)
while all variables will be accessible as environmental variables (System.getenv on Java-side).

To output any value stdout should be used. In case of Json you can access fields directly (f.e. `OUTPUT.your_field`).
If Catcher fails to parse json - it will use the whole output as a plain text.

In case of java script based step Catcher will run **nodeJs** (should be installed)

In case of Java/Kotlin source code files - Catcher will compile them first (**javac**/**kotlinc** should be installed).
It is extremely useful when you debug your step. Source code files should be placed in the root of resources folder. In
case of multiple classes - Catcher will compile them all.

MyClass::

    package jtest;

    import jtest.OtherClass;

    public class MyClass {

        public static void main(String[] args) {
            // works only with {"say": "<name>"}
            String name = args[0].split(":")[1].split("\"")[1];
            System.out.println(new OtherClass("hello " + name).arg);
        }
    }

OtherClass::

    package jtest;

    public class OtherClass {

        public String arg;

        public OtherClass(String arg) {
            this.arg = arg;
        }
    }

Test::

    variables:
        person: 'John Doe'
    steps:
        - MyClass.java:
            say: '{{ person }}'
            register: {greeting: '{{ OUTPUT }}'}
        - check: {equals: {the: '{{ greeting.strip() }}', is: 'hello John Doe'}}


.. toctree::
   :maxdepth: 4

   catcher
