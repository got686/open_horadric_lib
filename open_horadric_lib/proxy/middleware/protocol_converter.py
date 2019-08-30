from __future__ import annotations

import json
from enum import IntEnum

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
from google.protobuf.message import Message

import msgpack
from flask import request as flask_request
from flask.wrappers import Response
from werkzeug.http import parse_accept_header

from open_horadric_lib.context.proxy import ProxyContext
from open_horadric_lib.proxy.middleware.base import BaseProxyMiddleware


class ContentTypeString:
    JSON = "application/json"
    MSGPACK = "application/x-msgpack"
    PROTOBUF = "application/x-protobuf"
    WWW_FORM = "application/x-www-form-urlencoded"
    DEFAULT = "*/*"
    DEFAULT_APPLICATION = "application/*"
    EMPTY = ""


class ProtocolType(IntEnum):
    JSON = 0
    MSGPACK = 1
    PROTOBUF = 2


JSON_ACCEPT_TYPES = {
    ContentTypeString.JSON,
    ContentTypeString.DEFAULT,
    ContentTypeString.DEFAULT_APPLICATION,
}


class ProtocolConverterMiddleware(BaseProxyMiddleware):
    def process_request(self, request):
        if not flask_request.data:
            return {}

        protocol = self.get_input_protocol_type()
        if protocol == ProtocolType.MSGPACK:
            content = msgpack.loads(flask_request.data or b"\x80", raw=False)
            message = ParseDict(content, ProxyContext().request_message_type())
        elif protocol == ProtocolType.JSON:
            content = json.loads(flask_request.data or "{}")
            message = ParseDict(content, ProxyContext().request_message_type())
        elif protocol == ProtocolType.PROTOBUF:
            message = ProxyContext().request_message_type.FromString(flask_request.data)
        else:
            raise ValueError("Unexpected protocol type {}".format(protocol))

        return message

    def process_response(self, response: Message):
        protocol = self.get_output_protocol_type()
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

    @classmethod
    def get_output_protocol_type(cls) -> ProtocolType:
        accept_header = flask_request.headers.get("accept", ContentTypeString.DEFAULT)
        accept_formats = parse_accept_header(accept_header)
        accept_formats = sorted(accept_formats, key=lambda x: x[1], reverse=True)

        for accept_string, weight in accept_formats:
            if accept_string == ContentTypeString.MSGPACK:
                return ProtocolType.MSGPACK
            elif accept_string == ContentTypeString.PROTOBUF:
                return ProtocolType.PROTOBUF
            elif accept_string in JSON_ACCEPT_TYPES:
                return ProtocolType.JSON

        raise ValueError(f"Bad `accept` header {accept_header}")

    @classmethod
    def get_input_protocol_type(cls) -> ProtocolType:
        mime_type = flask_request.mimetype

        if mime_type == ContentTypeString.MSGPACK:
            return ProtocolType.MSGPACK
        elif mime_type == ContentTypeString.PROTOBUF:
            return ProtocolType.PROTOBUF
        elif mime_type in {ContentTypeString.JSON, ContentTypeString.EMPTY}:
            return ProtocolType.JSON
        else:
            raise ValueError(f"Bad mimetype for input data {mime_type}")
