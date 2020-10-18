import grpc
from concurrent import futures

import calculator_pb2
import calculator_pb2_grpc

import math


class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):

    def SquareRoot(self, request, context):
        response = calculator_pb2.Number()
        response.value = math.sqrt(request.value)
        return response


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
calculator_pb2_grpc.add_CalculatorServicer_to_server(CalculatorServicer(), server)
server.add_insecure_port('[::]:50051')
