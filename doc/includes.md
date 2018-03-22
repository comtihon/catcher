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
__Important__: variables in `include` will not be same as in `run` step. But you can supply it with variables:
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
        variables: 
    # .... some steps
```

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
steps:
    - echo: {from: '{{ RANDOM_STR }}', register: {uuid: '{{ OUTPUT }}'}}
    - http:
        actions:
          - post:  # register client and get id
              url: '{{ user_service_url }}/sign_up'
              headers: {Content-Type: 'application/json;charset=UTF-8'}
              body: {email: '{{ uuid + \'@test.com\' }}', name: 'TestUser', state: 'NEW'}
              response_code: 201
            register: {id: '{{ OUTPUT.data.id }}'}
          - post:  # fill some personal data
              url: '{{ user_service_url }}/data'
              headers: {Content-Type: 'application/json;charset=UTF-8'}
              body: {id: '{{ id }}', data: {gender: 'M', age: 22}}
```
And also you have `deposit_all_new_users.yaml` test, which requires at least one
new user to be registered. To solve this problem - include `register_user.yaml` and it 
will be run before the main test:
```yaml

---
include: register_user.yaml
steps:
    - http: 
        get:
          url: '{{ user_service_url }}/fetch_new_users'
        register: {users: '{{ OUTPUT.data.ids }}'}
    - kafka:
        produce:
          server: '{{ kafka }}'
          topic: 'message.bank_service.deposits'
          data: {user_ids: '{{ users }}'}
    - http:
        get:
          url: '{{ statistics_service }}/get_money_in_system'
        register: {money: '{{ OUTPUT.data.money }}'}
    - check: {equals: {the: '{{ money > 0 }}', is: true}}
```
__Important__: variables, registered in `include` statement will only be accessible for other 
includes.

# Run on action
What if you need to run action only after a specific actions of your test?  
Imagine you have `deposit_user.yaml` and you need to run `register_and_login` after several steps of your test:
```yaml

---
include: 
    file: register_and_login.yaml
    as: sign_up
variables:
    deposit: 1000
steps:
    - http:
        actions:
          - post:
              url: '{{ bank_admin_service }}/login'
              body: {user: '{{ admin_user }}', pass: ' {{ admin_pass }}'}
            register: {token: '{{ OUTPUT.token }}'}
          - post: # set auto deposit for all new users
              url: '{{ bank_admin_service }}/set_initial_deposit'
              headers: {token: '{{ token }}'}
              body: {data: '{{ deposit }}', currency: 'EUR'}
            register: {order_id: '{{ OUTPUT.data.id }}'}
    - wait: {seconds: 0.5}
    - kafka:
        produce:  # approve auto deposit (mocks external service)
          server: '{{ kafka_server }}'
          topic: '{{ deposit_admin_topic }}'
          data: {id: '{{ order_id }}', action: 'APPROVED'}
    - wait: {seconds: 0.5}
    - run: sign_up # register new user
    - kafka: 
        consume: 
            server: '{{ kafka_server }}'
            topic: '{{ registered_users_topic }}'
            where: # uuid var was computed during run step and is available now.
                equals: {the: '{{ MESSAGE.uuid }}', is: '{{ uuid }}'}
        register: {balance: '{{ OUTPUT.balance }}'}
    - check: {equals: {the: '{{ balance }}', is: '{{ deposit }}'}}  # test each new user gets 1000 eur deposit after sign_up
```

# Run parts on action
And now imagine you, in your test need to run only a part of `register_and_login.yaml` steps. How that is possible?  
First, let's change `register_and_login.yaml` to look like this:
```yaml

---
steps:
    - echo: {from: '{{ RANDOM_STR }}', register: {email: '{{ OUTPUT }}@test.com'}}
    - http:
        actions:
          - post:  # register client and get id
              url: '{{ user_service_url }}/sign_up'
              headers: {Content-Type: 'application/json'}
              body: {email: '{{ email }}', name: 'TestUser'}
              response_code: 201
            register: {token: '{{ OUTPUT.data.token }}'}
            tag: register
          - post:  # fill some personal data
              url: '{{ user_service_url }}/data'
              headers: {Content-Type: 'application/json', Authorization: '{{ token }}'}
              body: {gender: 'M', age: 22, firstName: 'John', lastName: 'Doe'}
            register: {uuid: '{{ OUTPUT.data.uuid }}'}
            tag: register
    - kafka:  # get password from kafka message, sent to email sender service
        consume: 
            server: '{{ kafka_server }}'
            topic: '{{ new_users_email_topic }}'
            where:
                equals: {the: '{{ MESSAGE.uuid }}', is: '{{ uuid }}'}
        register: {password: '{{ OUTPUT.password }}'}
        tag: register
    - http:
        post:
          url: '{{ user_service_url }}/login'
          headers: {Content-Type: 'application/json;charset=UTF-8'}
          body: {login: '{{ uuid }}', password: '{{ password }}'}
        register: {token: '{{ OUTPUT.data.token }}'}  # register token for another test's usage
        tag: login
    - echo: {from: 'Registered: {{ email }} with credentials {{ login }} : {{ password }}'}
```
We tagged important steps and can use it in test `deposit_only_new_logged_users.yaml` below:
```yaml

include: 
    file: register_and_login.yaml
    as: sign_up
variables:
    deposit: 1000
steps:
    - http:
        actions:
          - post:
              url: '{{ bank_admin_service }}/login'
              body: {user: '{{ admin_user }}', pass: ' {{ admin_pass }}'}
            register: {token: '{{ OUTPUT.token }}'}
          - post: # set auto deposit for all new users
              url: '{{ bank_admin_service }}/set_initial_deposit'
              headers: {token: '{{ token }}'}
              body: {data: '{{ deposit }}', currency: 'EUR'}
            register: {order_id: '{{ OUTPUT.data.id }}'}
    - wait: {seconds: 0.5}
    - kafka:
        produce:  # approve auto deposit (mocks external service)
          server: '{{ kafka_server }}'
          topic: '{{ deposit_admin_topic }}'
          data: {id: '{{ order_id }}', action: 'APPROVED'}
    - wait: {seconds: 0.5}
    - run: # register new user but don't run login
        include: sign_up.register
        variables:
          TODO
    - kafka: 
        consume: 
            server: '{{ kafka_server }}'
            topic: '{{ registered_users_topic }}'
            where: # uuid var was computed during run step and is available now.
                equals: {the: '{{ MESSAGE.uuid }}', is: '{{ uuid }}'}
        register: {balance: '{{ OUTPUT.balance }}'}
    - check: {equals: {the: '{{ balance }}', is: 0}}  # no gift for user without login
    TODO
```