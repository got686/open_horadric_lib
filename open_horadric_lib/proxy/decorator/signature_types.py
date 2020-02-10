from __future__ import annotations

from functools import wraps
from typing import Type

from flask.wrappers import Request

from google.protobuf.message import Message
from open_horadric_lib.base.context import Context


def signature_types(request_type: Type[Message], response_type: Type[Message]):
    def inner_function(func):
        @wraps(func)
        def wrapper(self, request: Request, context: Context):
            context.request_message_type = request_type
            context.response_message_type = response_type
            return func(self=self, request=request, context=context)

        return wrapper

    return inner_function
