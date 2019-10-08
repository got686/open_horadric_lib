from __future__ import annotations

import logging
from typing import List

import flask

from open_horadric_lib.client.client import BaseClient
from open_horadric_lib.proxy.middleware.base import BaseProxyMiddleware
from open_horadric_lib.proxy.middleware.protocol_converter import ProtocolConverterMiddleware
from open_horadric_lib.proxy.middleware.request_id import RequestIdProxyMiddleware


class BaseProxy:
    logger = logging.getLogger("open_horadric.proxy.BaseProxy")

    def __init__(self, client: BaseClient, middlewares: List[BaseProxyMiddleware] = None):
        if middlewares is None:
            middlewares = [RequestIdProxyMiddleware(), ProtocolConverterMiddleware()]

        self.client = client
        self.middlewares = middlewares

    def bind(self, app: flask.Flask):
        raise NotImplementedError
