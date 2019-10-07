from __future__ import annotations

import dataclasses

from open_horadric_lib.base.singleton import ThreadLocalSingletonMeta


@dataclasses.dataclass
class BaseContext(metaclass=ThreadLocalSingletonMeta):
    def reset(self):
        for field in dataclasses.fields(BaseContext):  # type: dataclasses.Field
            if field.default_factory is not dataclasses.MISSING:
                value = field.default_factory()
            elif field.default is not dataclasses.MISSING:
                value = field.default
            else:
                value = None
            setattr(self, field.name, value)
