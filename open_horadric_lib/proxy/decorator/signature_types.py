from __future__ import annotations

from functools import wraps
from typing import Type

from google.protobuf.message import Message

from open_horadric_lib.context.proxy import ProxyContext
from open_horadric_lib.proxy.decorator.base import convenient_decorator


@convenient_decorator
def signature_types(func, request_type: Type[Message], response_type: Type[Message]):
    @wraps(func)
    def wrapper(request):
        context = ProxyContext()
        context.request_message_type = request_type
        context.response_message_type = response_type

        return func(request)

    return wrapper
