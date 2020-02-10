from __future__ import annotations

import logging
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple

from google.protobuf.message import Message


class BaseClientMiddleware:
    logger = logging.getLogger("client.middleware")

    def apply(self, method: Callable[[Message, float, Any, Any], Message]) -> Callable[[Message, float, Any, Any], Message]:
        @wraps(method)
        def _wrapped(request: Message, timeout: float, metadata: Dict[str, str], credentials) -> Message:
            try:
                request = self._process_request(request=request, timeout=timeout, metadata=metadata, credentials=credentials)
                response = method(request=request, timeout=timeout, metadata=metadata, credentials=credentials)

                return self._process_response(response=response, request=request)

            except Exception as exception:
                return self._process_exception(exception=exception)

            finally:
                self._process_finally(request=request)

        return _wrapped

    def _process_request(self, request: Message, timeout: float, metadata: Optional[dict], credentials) -> Message:
        self.logger.debug("%s.process_request", repr(self))
        try:
            return self.process_request(request=request, timeout=timeout, metadata=metadata, credentials=credentials)
        except Exception as e:
            self.logger.exception("%s: process_request failed: %s", self, e)
            raise

    def _process_response(self, response: Message, request: Message) -> Message:
        self.logger.debug("%s.process_response", repr(self))
        try:
            return self.process_response(response=response, request=request)
        except Exception as e:
            self.logger.exception("%s: process_response failed: %s", self, e)
            raise

    def _process_exception(self, exception: Exception) -> Message:
        self.logger.debug("%s.process_exception", repr(self))
        try:
            return self.process_exception(exception=exception)
        except Exception as e:
            if e is not exception:
                self.logger.exception("%s: process_exception failed: %s", self, e)
            raise

    def _process_finally(self, request: Message) -> None:
        self.logger.debug("%s.process_finally", repr(self))
        try:
            return self.process_finally(request=request)
        except Exception as e:
            self.logger.exception("%s: process_finally failed: %s", self, e)
            raise

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_request(self, request: Message, timeout: float, metadata: Optional[dict], credentials) -> Message:
        return request

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_response(self, response: Message, request: Message) -> Message:
        return response

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_exception(self, exception: Exception) -> Message:
        raise exception

    def process_finally(self, request: Message) -> None:
        pass

    def __str__(self):
        return "<{}>".format(self.__class__.__name__)

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


def apply_middlewares(method: callable, *middlewares: Tuple[BaseClientMiddleware]) -> callable:
    for middleware in reversed(middlewares):  # type: BaseClientMiddleware
        method = middleware.apply(method)
    return method
