from __future__ import annotations

from flask import Flask
from open_horadric_lib.proxy.request import ProxyRequest


class ProxyApplication(Flask):
    request_class = ProxyRequest
