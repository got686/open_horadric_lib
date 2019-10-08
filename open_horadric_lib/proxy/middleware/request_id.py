from __future__ import annotations

import uuid

from flask import Request
from flask import Response

from open_horadric_lib.base.context import Context
from open_horadric_lib.proxy.middleware.base import BaseProxyMiddleware


class RequestIdProxyMiddleware(BaseProxyMiddleware):
    def process_request(self, request: Request, context: Context) -> Request:
        context.request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        return request

    def process_response(self, response: Response, context: Context) -> Response:
        response.headers["x-request-id"] = context.request_id
        return response
