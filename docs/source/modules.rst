Catcher Modular system
======================

Catcher has a flexible modular system. If built-in modules functionality is not enough you can use your own modules.
Read [tests](tests.md) for more info about running and naming steps, registering and using variables.
## Built-in
There are build in modules, shipped with catcher. You can learn about their syntax in :doc:`catcher.steps`.

## Additional
There are additional catcher modules available in this repository: https://github.com/comtihon/catcher_modules

## External
You can easily write your own modules and plug them to catcher:
1. write your module
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

To run it just tell the Catcher where your script is (it should be executable!):
`catcher your_test.yaml -m path/to/your/module`
Catcher will find your `math` module (by the step name) in `path/to/your/module` directory
and call it with `{"add": {"the": "1","to": "2"}}` argument. Your file's stdout will be the
step's `OUTPUT`.


.. toctree::
   :maxdepth: 4

   catcher
