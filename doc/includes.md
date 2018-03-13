# Includes philosophy
Ideally, every test needs to be done from scratch. If you are testing two user's interaction
you should first register to new users, and then run your tests. But putting user registration
code in every test is bulky.  
Catcher allows you to create one test (f.e. registration) and reuse it later!

# Syntax
* simple form will include just one file and run it automatically on include.
```yaml
include: register_user.yaml
```
* long form with variables override:
```yaml
include:
    file: register_user.yaml
    variables:
      user_email: 'override@email.org'
```
* array form with multiple includes, can contain both simple and long forms:
```yaml
include:
    - simple_form.yaml
    - file: long_form.yaml
      variables: {user_email: 'override@email.org'}
```
__Important__: in array form computed variables from one include is available in the next one:  
F.e. if `simple_form.yaml` registers variable `foo` = 123, `long_form.yaml` can access it.  
* include with alias - include can be `run` by alias:
```yaml
include:
    file: register_user.yaml
    as: sign_up
steps:
    # .... some steps
    - run: 
        include: sign_up
    # .... some steps
```
__Important__: you can run include by alias multiple times. When running by alias include file
will use your test's variables other then include ones. To override variables use:
```yaml
- run:
     include: sign_up
     variables:
        email: 'foo@baz.bar'
```
* include with alias and autorun - include will run by alias and on autorun:
```yaml
include:
    - file: clean_up_something.yaml
      as: clean
      variables:
        foo: bar
      run_on_include: true
steps:
    # .... some steps
    - run: 
        include: clean
    # .... some steps
```
__Important__: variables in `include` will not be same as in `steps`.
* partly include (simple form) - include only part of the test's steps:
```yaml
include:
    file: register_and_login.yaml
    as: sign_up
steps:
    - run:
        include: sign_up.register
```
* partly include (long form) - include only part of the test's steps (alias can contain dot):
```yaml
include:
    file: register_and_login.yaml
    as: sign.up
steps:
    - run:
        include: sign.up
        tag: register
```


# Simple run on include
Imagine you have this `register_user.yaml` test:

```yaml

---
variables:
    user_service_url: 'https://user_service.url'
steps:
    - echo: {from: '{{ RANDOM_STR }}', register: {uuid: '{{ OUTPUT }}'}}
    - http:
        actions:
          - post:  # register client and get id
              url: '{{ user_service_url }}/sign_up'
              headers: {Content-Type: 'application/json;charset=UTF-8'}
              body: {email: '{{ uuid + \'@test.com\' }}', name: 'TestUser'}
              response_code: 201
            register: {id: '{{ OUTPUT.data.id }}'}
          - post:  # fill some personal data
              url: '{{ user_service_url }}/data'
              headers: {Content-Type: 'application/json;charset=UTF-8'}
              body: {id: '{{ id }}', data: {gender: 'M', age: 22}}
```
And you need to register user before 
<TODO>


# Run on action
<TODO>


# Run parts on action
<TODO>
