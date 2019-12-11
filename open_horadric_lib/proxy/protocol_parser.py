from __future__ import annotations

from enum import IntEnum

from flask import request as flask_request
from werkzeug.http import parse_accept_header

from open_horadric_lib.base.exception import BadRequestFormat
from open_horadric_lib.base.exception import BadResponseFormat


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


JSON_ACCEPT_TYPES = {ContentTypeString.JSON, ContentTypeString.DEFAULT, ContentTypeString.DEFAULT_APPLICATION}


class ProtocolParser:
    def get_output_protocol_type(self) -> ProtocolType:
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

        raise BadResponseFormat(f"Bad `accept` header {accept_header}")

    def get_input_protocol_type(self) -> ProtocolType:
        mime_type = flask_request.mimetype

        if mime_type == ContentTypeString.MSGPACK:
            return ProtocolType.MSGPACK
        elif mime_type == ContentTypeString.PROTOBUF:
            return ProtocolType.PROTOBUF
        elif mime_type in {ContentTypeString.JSON, ContentTypeString.EMPTY}:
            return ProtocolType.JSON
        else:
            raise BadRequestFormat(format_=mime_type)
