# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import mapreduce_pb2 as mapreduce__pb2


class MapperStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Map = channel.unary_unary(
                '/mapreduce.Mapper/Map',
                request_serializer=mapreduce__pb2.MapRequest.SerializeToString,
                response_deserializer=mapreduce__pb2.MapReply.FromString,
                )


class MapperServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Map(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MapperServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Map': grpc.unary_unary_rpc_method_handler(
                    servicer.Map,
                    request_deserializer=mapreduce__pb2.MapRequest.FromString,
                    response_serializer=mapreduce__pb2.MapReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'mapreduce.Mapper', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Mapper(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Map(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/mapreduce.Mapper/Map',
            mapreduce__pb2.MapRequest.SerializeToString,
            mapreduce__pb2.MapReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class ReducerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Reduce = channel.unary_unary(
                '/mapreduce.Reducer/Reduce',
                request_serializer=mapreduce__pb2.ReduceRequest.SerializeToString,
                response_deserializer=mapreduce__pb2.ReduceReply.FromString,
                )


class ReducerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Reduce(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReducerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Reduce': grpc.unary_unary_rpc_method_handler(
                    servicer.Reduce,
                    request_deserializer=mapreduce__pb2.ReduceRequest.FromString,
                    response_serializer=mapreduce__pb2.ReduceReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'mapreduce.Reducer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Reducer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Reduce(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/mapreduce.Reducer/Reduce',
            mapreduce__pb2.ReduceRequest.SerializeToString,
            mapreduce__pb2.ReduceReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)