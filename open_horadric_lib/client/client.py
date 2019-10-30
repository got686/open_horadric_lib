from __future__ import annotations

import logging
from functools import wraps
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

from grpc import Channel
from grpc import ChannelCredentials

from google.protobuf.message import Message
from open_horadric_lib.client.middleware.base import BaseClientMiddleware
from open_horadric_lib.client.middleware.base import apply_middlewares


class BaseClient:
    """
    Abstract base class for gRPC clients.
    """

    __slots__ = ("channel", "_credentials", "middlewares")

    logger = logging.getLogger("open_horadric_lib.client")

    def __init__(
        self, channel: Channel, middlewares: List[BaseClientMiddleware] = None, credentials: ChannelCredentials = None
    ):
        if middlewares is None:
            middlewares = []

        self.channel = channel
        self._credentials = credentials
        self.middlewares = middlewares

    @property
    def credentials(self):
        return self._credentials

    def _wrap_method(self, method: Callable[[Message, float, Optional[dict], Any], Message]):
        @wraps(method)
        def last_method_wrapper(request: Message, timeout: Optional[float], metadata: Optional[dict], credentials):
            return method(request=request, timeout=timeout, metadata=metadata.items(), credentials=credentials)

        new_method = apply_middlewares(last_method_wrapper, *self.middlewares)

        @wraps(new_method)
        def first_method_wrapper(request: Message, timeout: Optional[float], metadata: Optional[dict], credentials):
            if metadata is None:
                metadata = {}

            return new_method(request=request, timeout=timeout, metadata=metadata, credentials=credentials)

        return first_method_wrapper
