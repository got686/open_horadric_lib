from __future__ import annotations

import logging
from functools import wraps
from typing import List
from typing import Type

from grpc import Server
from grpc import ServicerContext

from google.protobuf.message import Message
from open_horadric_lib.base.context import Context
from open_horadric_lib.server.middleware.base import BaseServerMiddleware
from open_horadric_lib.server.middleware.logging import LoggingServerMiddleware
from open_horadric_lib.server.middleware.request_id import RequestIdServerMiddleware


class BaseServerInterface:
    logger = logging.getLogger("open_horadric.server.BaseServer")
    context_class: Type[Context] = Context

    def __init__(self, middlewares: List[BaseServerMiddleware] = None):
        if middlewares is None:
            middlewares = [RequestIdServerMiddleware(), LoggingServerMiddleware()]

        self.middlewares = middlewares

    def _wrap_method(self, method):
        @wraps(method)
        def wrapper(request: Message, context: ServicerContext):
            request_context = self.context_class()
            request_context.rpc_context = context
            response = method(request=request, context=request_context)
            request_context.reset()
            return response

        return wrapper

    def bind(self, server: Server):
        raise NotImplementedError
