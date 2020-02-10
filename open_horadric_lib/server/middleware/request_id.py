from __future__ import annotations

import uuid

from google.protobuf.message import Message
from open_horadric_lib.base.context import Context
from open_horadric_lib.server.middleware.base import BaseServerMiddleware


class RequestIdServerMiddleware(BaseServerMiddleware):
    def process_request(self, request: Message, context: Context) -> Message:
        context.request_id = dict(context.rpc_context.invocation_metadata()).get("x-request-id", str(uuid.uuid4()))
        return request
