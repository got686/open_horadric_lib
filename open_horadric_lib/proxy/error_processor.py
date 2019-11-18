from __future__ import annotations

import json
import logging
from enum import IntEnum
from typing import Dict
from typing import Literal

import msgpack
from flask.wrappers import Response
from werkzeug.exceptions import HTTPException

from google.protobuf.empty_pb2 import Empty
from open_horadric_lib.base.context import Context
from open_horadric_lib.base.exception import BadResponseFormat
from open_horadric_lib.base.exception import BaseHoradricError
from open_horadric_lib.base.exception import BaseHttpError
from open_horadric_lib.base.exception import BaseLogicError
from open_horadric_lib.proxy.protocol_parser import ProtocolParser
from open_horadric_lib.proxy.protocol_parser import ProtocolType


class HttpCodes(IntEnum):
    OK = 200
    BAD_REQUEST = 400
    INTERNAL_ERROR = 500


ErrorResponseData = Dict[Literal["error", "message", "traceback"], str]


class ErrorProcessor:
    logger = logging.getLogger("open_horadric_lib.error")

    @classmethod
    def get_response_data(cls, exception: Exception) -> ErrorResponseData:
        if isinstance(exception, BaseHoradricError):
            return {"error": exception.text_code, "message": str(exception)}
        elif isinstance(exception, HTTPException):
            return {
                "error": exception.name.lower().replace(" ", "_"),
                "message": "{}: {}".format(exception.name, exception.description),
            }
        else:
            cls.logger.exception("Unexpected error")
            # TODO: add debug processing
            return {"error": "unexpected_error", "message": "Unexpected error"}

    @classmethod
    def create_response(cls, response_data: ErrorResponseData, protocol: ProtocolType, context: Context):
        headers = {"x-request-id": context.request_id}
        if protocol == ProtocolType.MSGPACK:
            content_type = "application/x-msgpack"
            content = msgpack.dumps(response_data)
            headers = {}
        elif protocol == ProtocolType.JSON:
            content_type = "application/json"
            content = json.dumps(response_data)
            headers = {}
        elif protocol == ProtocolType.PROTOBUF:
            content_type = "application/protobuf"
            content = Empty().SerializeToString()
            headers.update({"ERROR_CODE": response_data["error"], "ERROR_MESSAGE": response_data["message"]})
        else:
            raise ValueError(f"Unknown protocol: {protocol}")

        return Response(content, content_type=content_type, headers=headers)

    @classmethod
    def get_error_code(cls, exception: Exception):
        if isinstance(exception, BaseLogicError):
            return HttpCodes.INTERNAL_ERROR
        elif isinstance(exception, BaseHttpError):
            return exception.code
        elif isinstance(exception, HTTPException):
            return exception.code
        else:
            return HttpCodes.INTERNAL_ERROR

    @classmethod
    def process_error(cls, exception: Exception, context: Context):
        response_data = cls.get_response_data(exception=exception)

        try:
            protocol = ProtocolParser.get_output_protocol_type()
        except BadResponseFormat:
            protocol = ProtocolType.JSON

        response = cls.create_response(response_data=response_data, protocol=protocol, context=context)

        response.status_code = cls.get_error_code(exception=exception)

        return response
