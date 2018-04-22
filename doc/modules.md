# Modular system
Catcher has a flexible modular system. If built-in modules functionality is not enough you can use your own modules.  
Read [tests](tests.md) for more info about running and naming steps, registering and using variables. 
## Built-in
### checks - perform variable or condition check.  
Format:

    check:
        <check_operator>
You can find more about checks and check operators [here](checks.md).  
#### echo - debug variable to file or stdout.  
Format:

    echo: '{{ var }}'
or
    
    echo: {from: '{{ var }}', to: debug.output}
Echo is very useful, when you need to register some variables:  
```yaml

---
steps:
    - echo: {from: '{{ RANDOM_STR }}@test.com', register: {user_email: '{{ OUTPUT }}'}}
```
#### http - perform http request
Format:
```yaml
http: 
    <method>: 
        headers: <headers>
        url: 'http://test.com'
        response_code: 404
```
where `method` is http method name (`get`, `post`...), 
`response_code` is the code of response for step http to be successful. Default is `200`.  
`headers` is the dict of headers. You can skip it if empty.  
For methods with body (`post`, `put`) you should specify body:
```yaml
http: 
  post:
    headers: {Content-Type: 'application/json'}
    url: 'http://test.com'
    body: {'foo': bar}
```
Body can be any string or dict object (like in example above). If it is `dict` - it will be 
converted to `json` format.  
Body can also be load from file. In this case there is no conversions.
```yaml
http:
  post: 
    url: 'http://test.com'
    body_from_file: "data/answers.json"
```
#### kafka - interact with [kafka](https://kafka.apache.org/)
There is two actions available for kafka module:  
__Consume__ - read from kafka.  
Format:
```yaml
kafka: 
    consume: 
        server: '127.0.0.1:9092'
        group_id: 'test'
        topic: 'test_consume_with_timestamp'
        timeout: {seconds: 5}
        where: 
            equals: '{{ MESSAGE.timestamp > 1000 }}'
```
Where `server` is the kafka host. Can be multiple, comma-separated.  
`group_id` is the consumer group id. If not specified - `catcher` will be used.  
`topic` - the name of the topic, `timeout` is the consumer timeout (default is 1 sec). 
See `wait` step info for the format.  
__Produce__ - write to kafka.  
Format:
```yaml
kafka: 
    produce: 
        server: '127.0.0.1:9092'
        topic: 'test_produce_json'
        data: '{{ data|tojson }}'
```
Where `data` is the data to be produced.

#### postgres - interact with [postgres](https://www.postgresql.org/)
Format:
```yaml
postgres:
    request:
        conf: '{{ postgres }}'
        query: 'insert into test(id, num) values(3, 3);'
```
Where `conf` is a postgres configuration. Can be string or dict.  
Values: `dbname` - name of the database to connect to, `user` - database user, 
`host` database host, `password` user's password, `port` - database port.  
And `query` is any valid sql query.

#### run - run include on demand
Format:
```yaml
run: 
    include: test
    tag: <tag>
    variables: 
        file: other
```
Where `include` is the name of include, registered in `includes` and `variables` are the
variables to override. Can be skipped if empty.  
`tag` is the tag. If specified - will run only actions with this tag from include. Can also be 
set up via dot notation: `include: test.tag`.  
You can find more info [here](includes.md)

#### stop - stop the test
Can be used, if you need to stop the test without error.  
Format:
```yaml
stop:
    stop: 
        if: 
            <check_operator>
```
where <check_operator> is the same as in `checks`.  
Is useful if you use catcher for [migrations](migrations.md).
#### wait - wait
Format:
```yaml
wait: <wait>
```
where `wait` can be: `days`, `hours`, `minutes`, `seconds`, `microseconds`,
`milliseconds`, `nanoseconds`. You can use several at once:  
```yaml
wait: {minutes: 1, seconds: 30}
```
## External
You can easily write your own modules and plug them to catcher:  
1. write your module
2. use it in your test script
3. tell catcher where it is

For example you've developed a `math` module:
```bash
#!/bin/bash
one=$(echo ${1} | jq -r '.add.the')
two=$(echo ${1} | jq -r '.add.to')
echo $((${one} + ${two}))
```
to sum `the` and `to`.  
Then in test script you will write:
```yaml

---
variables:
  one: 1
  two: 2
steps:
    - math:
        add: {the: '{{ one }}', to: '{{ two }}'}
        register: {sum: '{{ OUTPUT }}'}
```
To run it just tell the Catcher where your script is (it should be executable!):  
`catcher your_test.yaml -m path/to/your/module`  
Catcher will find your `math` module (by the step name) in `path/to/your/module` directory
and call it with `{"add": {"the": "1","to": "2"}}` argument. Your file's stdout will be the
step's `OUTPUT`.