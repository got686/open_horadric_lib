from __future__ import annotations

import dataclasses
from typing import Type

from grpc import ServicerContext

from google.protobuf.message import Message
from open_horadric_lib.base.singleton import ThreadLocalSingletonMeta


@dataclasses.dataclass(init=False)
class Context(metaclass=ThreadLocalSingletonMeta):
    request_message_type: Type[Message]
    response_message_type: Type[Message]
    request_id: str
    rpc_context: ServicerContext
    metadata: dict = dataclasses.field(default_factory=dict)

    def reset(self):
        for field in dataclasses.fields(self.__class__):  # type: dataclasses.Field
            if field.default_factory is not dataclasses.MISSING:
                value = field.default_factory()
            elif field.default is not dataclasses.MISSING:
                value = field.default
            else:
                value = None
            setattr(self, field.name, value)
