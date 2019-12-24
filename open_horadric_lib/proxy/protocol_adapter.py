from __future__ import annotations

import json
from typing import TypeVar

import msgpack
from flask.wrappers import Request as FlaskRequest
from flask.wrappers import Response

import yaml
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
from google.protobuf.message import Message
from open_horadric_lib.base.context import Context
from open_horadric_lib.proxy.protocol_parser import ProtocolParser
from open_horadric_lib.proxy.protocol_parser import ProtocolType

MessageType = TypeVar("MessageType", bound=Message)


class ProtocolAdapter:
    def __init__(self, protocol_parser: ProtocolParser = None):
        if protocol_parser is None:
            protocol_parser = ProtocolParser()

        self.protocol_parser = protocol_parser

    def get_request(self, request: FlaskRequest, context: Context) -> MessageType:
        if not request.data:
            return context.request_message_type()

        protocol = self.protocol_parser.get_input_protocol_type()
        if protocol == ProtocolType.MSGPACK:
            content = msgpack.loads(request.data or b"\x80", raw=False)
            message = ParseDict(content, context.request_message_type())
        elif protocol == ProtocolType.JSON:
            content = json.loads(request.data or "{}")
            message = ParseDict(content, context.request_message_type())
        elif protocol == ProtocolType.YAML:
            content = yaml.safe_load(request.data or "{}")
            message = ParseDict(content, context.request_message_type())
        elif protocol == ProtocolType.PROTOBUF:
            message = context.request_message_type.FromString(request.data)
        else:
            raise ValueError("Unexpected protocol type {}".format(protocol))

        return message

    def make_response(self, response: MessageType, context: Context):
        protocol = self.protocol_parser.get_output_protocol_type()
        if protocol == ProtocolType.MSGPACK:
            content_type = "application/x-msgpack"
            content = msgpack.dumps(MessageToDict(response))
        elif protocol == ProtocolType.JSON:
            content_type = "application/json"
            content = json.dumps(MessageToDict(response))
        elif protocol == ProtocolType.YAML:
            content_type = "application/x-yaml"
            content = yaml.dump(MessageToDict(response))
        elif protocol == ProtocolType.PROTOBUF:
            content_type = "application/x-protobuf"
            content = response.SerializeToString()
        else:
            raise ValueError("Unexpected protocol type {}".format(protocol))

        return Response(content, content_type=content_type)
