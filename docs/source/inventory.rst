Inventories
===========
Inventory file is a file where you set up most common variables, like hosts, credentials and urls.
You can run your tests without inventories, but they are recommended if you have multiple environments to test.
Example
-------
Here is `dev_inventory.yaml`::

    ---
    kafka_server: 'kafka.dev.host.de'
    deposit_admin_topic: 'admin_service.deposits'
    bank_admin_service: 'http://bank_admin.dev.host.de'
    admin_user: 'Admin'
    admin_pass: 'qwerty'
And here is the test using it::


    ---
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

To run test with specified inventory use `-i` parameter: `catcher -i inventory/dev_inventory.yaml tests`
