from os.path import dirname, join

from catcher.steps.step import Step, update_variables
from catcher.utils import module_utils
from catcher.utils import file_utils
from catcher.utils.misc import fill_template, fill_template_str, try_get_objects


class GRPC(Step):
    """
    Perform a remote procedure call with protobuffers layer.

    :Input:

    :call: Make a remote procedure call

    - url: server url
    - function: service and method you are going to call separated by dot. Case insensitive (MyClass.my_function)
    - schema: path to the .proto resource file. *Optional* Ignore it if reflection is configured on the
      server side
    - data: data to pass. *Optional*

    :Examples:
    calculator.proto
    ::

        message Number {
            float value = 1;
        }

        service Calculator {
            rpc SquareRoot(Number) returns (Number) {}
        }

    test
    ::

        grpc:
            call:
                url: 'localhost:50051'
                function: calculator.squareroot
                schema: 'calculator.proto'
                data: {'value': 2}
            register: {'my_value': '{{ OUTPUT.value }}'

    Complex schema case::

        grpc:
            call:
                url: 'localhost:50051'
                function: greeter.greet
                schema: 'greeter.proto'
                data:
                    result:
                        url: '{{ my_url }}'
                        title: 'test'
                        snippets: 'test2'
            register: {value: '{{ OUTPUT.name }}'}

    Useful tip: if you'd like to use templates in your .proto file - do not do it in the original resources, as Catcher
    shouldn't modify them. Use echo step to fill a template and create another .proto file for you.
    """

    def __init__(self, call=None, **kwargs) -> None:
        super().__init__(**kwargs)
        if call:
            [service, method] = call['function'].split('.')
            self.service = service.lower()
            self.url = call['url']
            self.method = method.lower()
            self.schema = call.get('schema')
            self.data = call.get('data', {})

    @update_variables
    def action(self, includes: dict, variables: dict) -> dict or tuple:
        import grpc
        channel = grpc.insecure_channel(fill_template(self.url, variables))
        if self.schema:
            self._compile_proto_files(variables)
            client = self._open_channel(channel, variables)
            method, input_arg = self._compose_arg(variables)
            return variables, getattr(client, method)(input_arg)
        else:
            raise Exception('Reflection not supported (yet)')

    def _compile_proto_files(self, variables):
        """
        Compile .proto resource into the definition (_pb2) and client code (_pb2_grpc)
        """
        from grpc.tools import command
        schema = fill_template(self.schema, variables)
        command.build_package_protos(join(variables['RESOURCES_DIR'], dirname(schema)), strict_mode=True)

    def _open_channel(self, channel, variables):
        """
        Search for stub in generated module _pb2_grpc. Instantiate it with channel and return.
        """
        schema = fill_template(self.schema, variables)
        mod = module_utils.load_external_actions(join(variables['RESOURCES_DIR'],
                                                      file_utils.get_filename(schema) + '_pb2_grpc.py'))
        classes = module_utils.get_all_classes(mod)
        classes = {k.lower(): v for k, v in classes.items()}
        stub = classes.get(fill_template(self.service, variables) + 'stub')
        if not stub:
            raise Exception('Can\'t find stub in generated code. Something went wrong')
        return stub(channel)

    def _compose_arg(self, variables):
        """
        Search for the method in generated _pb2. Resolve input type by the method's input.
        """
        schema = fill_template(self.schema, variables)
        service = fill_template(self.service, variables)
        method = fill_template(self.method, variables)
        # search for the service
        mod = module_utils.load_external_actions(join(variables['RESOURCES_DIR'],
                                                      file_utils.get_filename(schema) + '_pb2.py'))
        services = {str(k).lower(): v for k, v in mod.DESCRIPTOR.services_by_name.items()}
        service = services.get(service)
        if not service:
            raise Exception('Unable to find service {} in {}'.format(service,
                                                                     file_utils.get_filename(schema) + '_pb2'))
        # find service's method
        methods = dict([(f.name.lower(), f) for f in service.methods])
        method = methods.get(method)
        if not method:
            raise Exception('No method {} in service {}'.format(method, service))
        # find method's input type
        input_type = method.input_type
        classes = module_utils.get_all_classes(mod)
        data = try_get_objects(fill_template_str(self.data, variables))
        return method.name, classes[input_type.name](**data)
