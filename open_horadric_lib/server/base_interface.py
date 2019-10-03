from __future__ import annotations

import logging
from typing import List

from grpc import Server

from open_horadric_lib.server.middleware.base import BaseServerMiddleware


class BaseServerInterface:
    logger = logging.getLogger("open_horadric.server.BaseServer")

    def __init__(self, middlewares: List[BaseServerMiddleware]):
        self.middlewares = middlewares

    def bind(self, server: Server):
        raise NotImplementedError
