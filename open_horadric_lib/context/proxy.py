from __future__ import annotations

from typing import Type

from google.protobuf.message import Message

from open_horadric_lib.context.base import BaseContext


class ProxyContext(BaseContext):
    def __init__(self):
        self.request_message_type: Type[Message] = None
        self.response_message_type: Type[Message] = None
        self.request_id: str = None

    def clean(self):
        self.request_message_type = None
        self.response_message_type = None
        self.request_id = None
