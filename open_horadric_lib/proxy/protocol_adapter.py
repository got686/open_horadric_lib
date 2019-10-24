from __future__ import annotations

import json
from typing import TypeVar

import msgpack
from flask.wrappers import Request as FlaskRequest
from flask.wrappers import Response

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
from google.protobuf.message import Message
from open_horadric_lib.base.context import Context
from open_horadric_lib.proxy.protocol_parser import ProtocolParser
from open_horadric_lib.proxy.protocol_parser import ProtocolType

MessageType = TypeVar("MessageType", bound=Message)


class ProtocolAdapter:
    @staticmethod
    def get_request(request: FlaskRequest, context: Context) -> MessageType:
        if not request.data:
            return context.request_message_type()

        protocol = ProtocolParser.get_input_protocol_type()
        if protocol == ProtocolType.MSGPACK:
            content = msgpack.loads(request.data or b"\x80", raw=False)
            message = ParseDict(content, context.request_message_type())
        elif protocol == ProtocolType.JSON:
            content = json.loads(request.data or "{}")
            message = ParseDict(content, context.request_message_type())
        elif protocol == ProtocolType.PROTOBUF:
            message = context.request_message_type.FromString(request.data)
        else:
            raise ValueError("Unexpected protocol type {}".format(protocol))

        return message

    @staticmethod
    def make_response(response: MessageType, context: Context):
        protocol = ProtocolParser.get_output_protocol_type()
        if protocol == ProtocolType.MSGPACK:
            content_type = "application/x-msgpack"
            content = msgpack.dumps(MessageToDict(response))
        elif protocol == ProtocolType.JSON:
            content_type = "application/json"
            content = json.dumps(MessageToDict(response))
        elif protocol == ProtocolType.PROTOBUF:
            content_type = "application/protobuf"
            content = response.SerializeToString()
        else:
            raise ValueError("Unexpected protocol type {}".format(protocol))

        return Response(content, content_type=content_type)
