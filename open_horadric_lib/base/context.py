from __future__ import annotations

import dataclasses
from typing import Type

from grpc import ServicerContext

from google.protobuf.message import Message
from open_horadric_lib.base.singleton import ThreadLocalSingletonMeta


@dataclasses.dataclass()
class Context(metaclass=ThreadLocalSingletonMeta):
    request_message_type: Type[Message] = None
    response_message_type: Type[Message] = None
    request_id: str = ""
    rpc_context: ServicerContext = None
    _metadata: dict = None
    service_name: str = ""
    method_name: str = ""

    @property
    def metadata(self) -> dict:
        if self._metadata is None and self.rpc_context is not None:
            self._metadata = dict(self.rpc_context.invocation_metadata())

        return self._metadata

    def reset(self):
        for field in dataclasses.fields(self.__class__):  # type: dataclasses.Field
            if field.default_factory is not dataclasses.MISSING:
                value = field.default_factory()
            elif field.default is not dataclasses.MISSING:
                value = field.default
            else:
                value = None
            setattr(self, field.name, value)
