# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: videoservice.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12videoservice.proto\x12\x0cvideoservice\"-\n\rDecodeRequest\x12\r\n\x05video\x18\x01 \x01(\x0c\x12\r\n\x05s3key\x18\x02 \x01(\t\"%\n\x0b\x44\x65\x63odeReply\x12\x16\n\x0e\x63lassification\x18\x01 \x01(\t\"0\n\x10RecogniseRequest\x12\r\n\x05\x66rame\x18\x01 \x01(\x0c\x12\r\n\x05s3key\x18\x02 \x01(\t\"(\n\x0eRecogniseReply\x12\x16\n\x0e\x63lassification\x18\x01 \x01(\t2R\n\x0cVideoDecoder\x12\x42\n\x06\x44\x65\x63ode\x12\x1b.videoservice.DecodeRequest\x1a\x19.videoservice.DecodeReply\"\x00\x32`\n\x11ObjectRecognition\x12K\n\tRecognise\x12\x1e.videoservice.RecogniseRequest\x1a\x1c.videoservice.RecogniseReply\"\x00\x42H\n\x19\x63om.vhive.video_analyticsB\x0cvideoserviceP\x01Z\x1btests/video_analytics/protob\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'videoservice_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\031com.vhive.video_analyticsB\014videoserviceP\001Z\033tests/video_analytics/proto'
  _globals['_DECODEREQUEST']._serialized_start=36
  _globals['_DECODEREQUEST']._serialized_end=81
  _globals['_DECODEREPLY']._serialized_start=83
  _globals['_DECODEREPLY']._serialized_end=120
  _globals['_RECOGNISEREQUEST']._serialized_start=122
  _globals['_RECOGNISEREQUEST']._serialized_end=170
  _globals['_RECOGNISEREPLY']._serialized_start=172
  _globals['_RECOGNISEREPLY']._serialized_end=212
  _globals['_VIDEODECODER']._serialized_start=214
  _globals['_VIDEODECODER']._serialized_end=296
  _globals['_OBJECTRECOGNITION']._serialized_start=298
  _globals['_OBJECTRECOGNITION']._serialized_end=394
# @@protoc_insertion_point(module_scope)