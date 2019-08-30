from __future__ import annotations

from open_horadric_lib.base.singleton import ThreadLocalSingletonMeta


class BaseContext(metaclass=ThreadLocalSingletonMeta):
    pass
