from __future__ import annotations

from flask.wrappers import Request

__all__ = ("ProxyRequest",)


class ProxyRequest(Request):
    @property
    def data(self):
        # No form parse in no content-type header case because in that case request.data is empty string
        if self.disable_data_descriptor:
            raise AttributeError("data descriptor is disabled")
        return self.get_data()
