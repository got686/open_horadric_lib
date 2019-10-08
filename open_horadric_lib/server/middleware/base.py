from __future__ import annotations

import logging
from functools import wraps
from typing import Callable
from typing import Tuple

from grpc import ServicerContext

from google.protobuf.message import Message
from open_horadric_lib.base.context import Context


class BaseServerMiddleware:
    logger = logging.getLogger("server.middleware")

    def apply(
        self, method: Callable[[Message, Context, ServicerContext], Message]
    ) -> Callable[[Message, Context, ServicerContext], Message]:
        @wraps(method)
        def _wrapped(request: Message, context: Context) -> Message:
            try:
                request = self._process_request(request=request, context=context)
                response = method(request=request, context=context)

                return self._process_response(response=response, request=request, context=context)

            except Exception as exception:
                return self._process_exception(exception, context=context)

            finally:
                self._process_finally(request=request, context=context)

        return _wrapped

    def _process_request(self, request: Message, context: Context) -> Message:
        self.logger.debug("%s.process_request", repr(self))
        try:
            return self.process_request(request=request, context=context)
        except Exception as e:
            self.logger.exception("%s: process_request failed: %s", self, e)
            raise

    def _process_response(self, response: Message, request: Message, context: Context) -> Message:
        self.logger.debug("%s.process_response", repr(self))
        try:
            return self.process_response(response=response, request=request, context=context)
        except Exception as e:
            self.logger.exception("%s: process_response failed: %s", self, e)
            raise

    def _process_exception(self, exception: Exception, context: Context) -> Message:
        self.logger.debug("%s.process_exception", repr(self))
        try:
            return self.process_exception(exception=exception, context=context)
        except Exception as e:
            if e is not exception:
                self.logger.exception("%s: process_exception failed: %s", self, e)
            raise

    def _process_finally(self, request: Message, context: Context) -> None:
        self.logger.debug("%s.process_finally", repr(self))
        try:
            return self.process_finally(request=request, context=context)
        except Exception as e:
            self.logger.exception("%s: process_finally failed: %s", self, e)
            raise

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_request(self, request: Message, context: Context) -> Message:
        return request

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_response(self, response: Message, context: Context, request: Message) -> Message:
        return response

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_exception(self, exception: Exception, context: Context) -> Message:
        raise exception

    def process_finally(self, request: Message, context: Context) -> None:
        pass

    def __str__(self):
        return "<{}>".format(self.__class__.__name__)

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


def apply_middlewares(method: callable, *middlewares: Tuple[BaseServerMiddleware]) -> callable:
    for middleware in reversed(middlewares):  # type: BaseServerMiddleware
        method = middleware.apply(method)
    return method
