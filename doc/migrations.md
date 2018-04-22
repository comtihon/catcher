# Use Catcher as universal migration tool.
Imagine you have several microservices and you've developed a new feature. To deploy
this feature to any environment you should manually run several actions:  
1. load <new_template.pdf> to s3.
2. run sql migration on service1's postgres
3. run n1ql migration on service2's couchbase
4. notify all services of new template via kafka

Of course, you can move this steps to different microservices, f.e. step 2 will be in service1
migration, step 3 in service 2 migration etc...  
But it will lead to splitting migration or code duplication and can lead to errors.  

## Migration
`sub_steps/migration.yaml`
```yaml

steps:
    - postgres:
        request:
            conf: '{{ migrations_postgres }}'
            query: "select count(*) from migration where hash = '{{ TEST_NAME }}';"
        register: {result: '{{ OUTPUT }}'}
        tag: check
        name: 'check_migration_{{ TEST_NAME }}'
    - stop: 
        if: 
            equals: {the: '{{ result }}', is: 1}
        tag: check
        name: 'stop_if_already_run_{{ TEST_NAME }}'
    - postgres:
        request:
            conf: '{{ migrations_postgres }}'
            query: "insert into migration(id, hash) values(1, '{{ TEST_NAME }}');"
        tag: commit
        name: 'commit_migration_{{ TEST_NAME }}'
```
`migrations/migration1.yaml`
```yaml

---
include: 
    file: sub_steps/migration.yaml
    as: migrate
variables:
  new_template: new_template.pdf
steps:
  - run: migrate.check
  - aws:
      load: 
        config: '{{ config }}'
        the: '{{ new_template }}'
        to: '{{ path_to_aws }}'
      register: {template_path: '{{ OUTPUT.path }}'}
      name: 'load template {{ new_template }} to the aws'
  - postgres:
      request:
        conf: '{{ service1_postgres }}'
        query: "insert into templates(name, path) values({{ new_template }}, {{template_path}});"
      name: 'enable {{ new_template }} for service1'
  - couchbase:
      request:
        conf: '{{ service2_couchbase }}'
        query: "insert into templates(key, value) values 
        ('{{ new_template }}', {'file': '{{ new_template }}', 'path': '{{ template_path }}' }"
      name: 'enable {{ new_template }} for service2'
  - kafka:
      produce:
        produce: 
            server: '{{ kafka_bus }}'
            topic: 'configuration_changes'
            data: '{"type":"TEMPLATE","action":"RELOAD","path":"{{ template_path}} }'
        name: 'notify all about new template {{ new_template }}'
  - run: migrate.commit
```
This will run all steps between `migrate.check` and `migrate.commit` once.

## Rollbacks
To use rollbacks you have to change your migrations. Above, the optimistic way of using 
migrations was described. You just create your migrations, put them in `migrations` folder
and run via `catcher -i inventory migrations -m modules`.  
To use rollbacks you will have to write you migration with tag `up` and `down` on every step:
`migration1.yaml`
```yaml

---
include:
    file: sub_steps/migration.yaml
    as: migrate
steps:
    - run: migrate.check
      tag: up
    - aws:
        load: 
          config: '{{ config }}'
          the: '{{ new_template }}'
          to: '{{ path_to_aws }}'
        register: {template_path: '{{ OUTPUT.path }}'}
        name: 'load template {{ new_template }} to the aws'
        tag: up
    - aws:
        delete: 
          config: '{{ config }}'
          the: '{{ new_template }}'
        name: 'delete template {{ new_template }} from the aws'
        tag: down
    # ... other steps up and down
    - run: migrate.commit
      tag: up
```
Then you will have to create main migration file:
```yaml

---
include:
    - file: sub_steps/migration.yaml
      as: migrate 
    - file: migration1.yaml
      as: migration1
steps:
  - run: migration1.up
```
Main migration file will collect all your migrations and you will run them via 
`catcher -i inventory main_migration.yaml -m modules`.  
To run rollbacks you will have to create the same rollback file where you will run
only `down` tags of the test.