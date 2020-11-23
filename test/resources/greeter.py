import grpc
from concurrent import futures

import greeter_pb2
import greeter_pb2_grpc


class GreeterServicer(greeter_pb2_grpc.GreeterServicer):

    def Echo(self, request, context):
        response = greeter_pb2.HelloResponse()
        response.name = request.name
        return response

    def Greet(self, request, context):
        response = greeter_pb2.HelloResponse()
        response.name = 'Result for ' + request.result.title + ' contains ' + request.result.snippets
        return response


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
greeter_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
server.add_insecure_port('[::]:50051')
