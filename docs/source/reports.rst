Reports - Catcher's trace files
===============================

Sometimes even with ``-l debug`` flag output is not that clear. What is your test doing? Why the variable has exact this
value and where does it come from? Test reports have all answers.

How to create
-------------
Let's reproduce a situation which is easy to meet and hard to solve. You have a test which includes one or more other
tests. At some point you notice that it is not working correctly. Looks like include or some other test overrides
variables!

Let's start with **include.yaml**::

    steps:
    - echo:
        from: '{{ fname }}_{{ lname }}@example.com'
        register: {'email': '{{ OUTPUT }}'}
        name: 'Register email as a {{ email }}'

All it does is transforms first and last name to the email and introduces a new variable **email**.

The test itself::

    variables:
        email:  '{{ random("email") }}'
        fname: '{{ random("first_name") }}'
        lname: '{{ random("last_name") }}'
    include:
        file: include.yaml
        as: simple
    steps:
        - echo: 'email is {{ email }}'
        - run: 'simple'
        - echo: 'email is {{ email }}'

As you may see the main test already has a random **email** defined in the variables section. And somewhere in the middle
of the test it changes. Let's form a report to find where.

Since Catcher **1.36.0** html format for reports is supported, which is more human-friendly.
I advice to leave json for machine-machine integration and use html for day-to-day life.

Run Catcher with ``--format html`` (available since 1.36)::

    catcher -i inventory/dev_inventory.yaml --format html tests/my_complex_test.yaml

Run Catcher with ``--format json`` (versions up to 1.35 support only **json**)::

    catcher -i inventory/dev_inventory.yaml --format json tests/my_complex_test.yaml

It will run your test and create a report file in ``reports`` directory.

How to read: HTML
-----------------
The root report for html is **reports/index.html** file. Open it in your browser. For the example test above it will
show you:

.. image:: https://raw.githubusercontent.com/comtihon/catcher/master/docs/_static/index.png

This is the main test report. Each testcase is mentioned in the separate row. Includes, which run before the testcase
are shown in the separate row before the test they were included from. Named includes which you run via :meth:`catcher.steps.run`
are displayed as steps.

From this page you can:

- navigate to testcases source
- navigate to test run's details to investigate a problem
- see the system information

.. image:: https://raw.githubusercontent.com/comtihon/catcher/master/docs/_static/details.png

This is the test run details page. As you can see all three steps of your example test succeeded.
You can explore the variables, registered **after** each step. It is very useful, when you are trying to understand why
your test is not working as expected.

.. image:: https://raw.githubusercontent.com/comtihon/catcher/master/docs/_static/log.png

This is the test run's full log. Sometimes just checking variables after each step is not enough and you need more information.
Here it is. It contains log statements, outputs, steps definitions and variables. Included substeps are also described here.
Actual steps are highlighted with green (passed) and red (failed) colors.

.. image:: https://raw.githubusercontent.com/comtihon/catcher/master/docs/_static/system.png

The last thing is system output. This is the information gathered from the system tests are running in. Can be useful if
everything is OK locally, but fails in CI or for other engineers.

It contains system information, all loaded `steps <https://catcher-test-tool.readthedocs.io/en/latest/source/steps.html>`_
including external and custom ones, all `modules <https://catcher-test-tool.readthedocs.io/en/latest/source/catcher.modules.html>`_,
`filters <https://catcher-test-tool.readthedocs.io/en/latest/source/filters_and_functions.html#filters>`_ and
`functions <https://catcher-test-tool.readthedocs.io/en/latest/source/filters_and_functions.html#functions>`_,
including custom implementations. If you are going to share test results make sure to archive the whole reports directory,
together with this system log.

How to read: JSON
-----------------
Let's open **report_<timestamp>.json** file. You'll see a list of json objects. For every test run - there will be an
object in the top list. In our case - there will be only one object::


    [
      {
        "end_time": "2020-09-07 18:45:59",
        "start_time": "2020-09-07 18:45:59",
        "file": "test.yml",
        "type": "test",
        "output": [
          <OUTPUT>
        ],
        "status": "OK",
        "comment": null
      }
    ]

| **start_time** - when test started.
| **end_time** - when test ended.
| **file** - which test was it.
| **type** - can be a **test** or a **test_cleanup** in case of final actions.
| **output** - the actual trace information for all steps within this test.
| **status** - **OK** - test finishes successfully, **FAIL** - test failed, other message - also failed.
| **comment** - comment, which Catcher may leave for your test. Usually it is **Skipped** if test was skipped.

Let's go through the report and check the output.

Start step information. Every started step will have this event::

    {
        "time": "2020-09-07 18:45:59",
        "step": {
          "echo": "email is {{ email }}"
        },
        "variables": {
          "CURRENT_DIR": "/home/val/new_dir",
          "RESOURCES_DIR": "/home/val/new_dir/resources",
          "TEST_NAME": "test.yml",
          "email": "allengill@jones.com",
          "fname": "James",
          "lname": "Camacho"
        },
        "nested": 0
    }

| **time** - when it started
| **step** - which step was it
| **variables** - all variables which were sent to this step as start variables
| **nested** - used to determine include level. For the main test nested will always be 0. If you include and run other tests
 - their nested will be +1 for every include in include.

Information from logger::

    {
        "time": "2020-09-07 18:45:59",
        "data": "No module named 'allengill'",
        "level": "debug"
    }

| **time** - when the event took place.
| **data** - actual output.
| **level** - log level, used by the step which printed this information.

If you develop your own steps in Python and would like them to pass output to the reports system - use
:meth:`catcher.utils.logger` functions instead of the default ones.

Output of **echo** step looks the same, as echo just uses logger::

    {
        "time": "2020-09-07 18:45:59",
        "data": "email is allengill@jones.com",
        "level": "info"
    }

The only difference - it will always have **info** level.

Short step report information. When step finished it says to the console OK or Fail::

    {
        "time": "2020-09-07 18:45:59",
        "data": "Step echo [0s]\u001b[32m OK\u001b[0m",
        "level": "info"
    }
It is the same as simple output. Catcher will record every event you see in the console. If you use colored output (used
by default) - you'll see special characters (color codes) in the output.

End step - every step which ends has this event and it is the most interesting for us::

    {
        "time": "2020-09-07 18:45:59",
        "step": {
          "echo": "email is {{ email }}"
        },
        "variables": {
          "CURRENT_DIR": "/home/val/new_dir",
          "RESOURCES_DIR": "/home/val/new_dir/resources",
          "TEST_NAME": "test.yml",
          "email": "allengill@jones.com",
          "fname": "James",
          "lname": "Camacho"
        },
        "nested": 0,
        "success": true,
        "output": null
    }

| It has the same fields as start step event + one additional:
| **success** - determines if step was successful

By comparing start step event variables with end event variables we can find the difference. For example in our case
**echo** step from the other included test's input::

    {
        "time": "2020-09-07 18:45:59",
        "step": {
          "echo": {
            "from": "{{ fname }}_{{ lname }}@example.com",
            "register": {
              "email": "{{ OUTPUT }}"
            },
            "name": "Register email as a {{ email }}"
          }
        },
        "variables": {
          "CURRENT_DIR": "/home/val/new_dir",
          "RESOURCES_DIR": "/home/val/new_dir/resources",
          "TEST_NAME": "test.yml",
          "email": "allengill@jones.com",
          "fname": "James",
          "lname": "Camacho"
        },
        "nested": 1
    }

In **variables** email is **allengill@jones.com**.

And output::

    {
        "time": "2020-09-07 18:45:59",
        "step": {
          "echo": {
            "from": "{{ fname }}_{{ lname }}@example.com",
            "register": {
              "email": "{{ OUTPUT }}"
            },
            "name": "Register email as a {{ email }}"
          }
        },
        "variables": {
          "CURRENT_DIR": "/home/val/new_dir",
          "RESOURCES_DIR": "/home/val/new_dir/resources",
          "TEST_NAME": "test.yml",
          "email": "James_Camacho@example.com",
          "fname": "James",
          "lname": "Camacho"
        },
        "nested": 1,
        "success": true,
        "output": null
    }

In output variables **email** is **James_Camacho@example.com**!

