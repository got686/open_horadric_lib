from __future__ import annotations

import json
import logging
from enum import IntEnum

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


class ErrorProcessor:
    logger = logging.getLogger("open_horadric_lib.error")

    @classmethod
    def process_error(cls, exception: Exception, context: Context):
        if isinstance(exception, BaseHoradricError):
            response_data = {"error": exception.text_code, "message": str(exception)}
        elif isinstance(exception, HTTPException):
            response_data = {
                "error": exception.name.lower().replace(" ", "_"),
                "message": "{}: {}".format(exception.name, exception.description),
            }
        else:
            cls.logger.exception("Unexpected error")
            response_data = {"error": "unexpected_error", "message": "Unexpected error"}

            # TODO: add debug processing
            # response_data["traceback"] = traceback.format_exc()

        try:
            protocol = ProtocolParser.get_output_protocol_type()
        except BadResponseFormat:
            protocol = ProtocolType.JSON

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

        response = Response(content, content_type=content_type, headers=headers)

        if isinstance(exception, BaseLogicError):
            response.status_code = cls.get_error_code(exception=exception)
        elif isinstance(exception, BaseHttpError):
            response.status_code = exception.code
        elif isinstance(exception, HTTPException):
            response.status_code = exception.code
        else:
            response.status_code = HttpCodes.INTERNAL_ERROR

        return response

    # noinspection PyUnusedLocal
    @staticmethod
    def get_error_code(exception):
        return HttpCodes.INTERNAL_ERROR
