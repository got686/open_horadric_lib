from __future__ import annotations

import logging
from functools import wraps
from typing import Callable
from typing import Optional
from typing import Tuple

from flask.wrappers import Request
from flask.wrappers import Response

from open_horadric_lib.base.context import Context


class BaseProxyMiddleware:
    logger = logging.getLogger("proxy.middleware")

    def apply(self, method):
        @wraps(method)
        def _wrapped(request: Request, context: Context) -> Callable[[Request, Context], Response]:
            try:
                request = self._process_request(request, context=context)
                response = method(request=request, context=context)

                return self._process_response(response, context=context)

            except Exception as exception:
                return self._process_exception(exception, context=context)

            finally:
                self._process_finally(context=context)

        return _wrapped

    def _process_request(self, request: Request, context: Context) -> Request:
        self.logger.debug("%s.process_request", repr(self))
        try:
            return self.process_request(request, context=context)
        except Exception as e:
            self.logger.exception("%s: process_request failed: %s", self, e)
            raise

    def _process_response(self, response: Response, context: Context) -> Response:
        self.logger.debug("%s.process_response", repr(self))
        try:
            return self.process_response(response, context=context)
        except Exception as e:
            self.logger.exception("%s: process_response failed: %s", self, e)
            raise

    def _process_exception(self, exception: Exception, context: Context) -> Optional[Response]:
        self.logger.debug("%s.process_exception", repr(self))
        try:
            return self.process_exception(exception, context=context)
        except Exception as e:
            if e is not exception:
                self.logger.exception("%s: process_exception failed: %s", self, e)
            raise

    def _process_finally(self, context: Context) -> None:
        self.logger.debug("%s.process_finally", repr(self))
        try:
            return self.process_finally(context=context)
        except Exception as e:
            self.logger.exception("%s: process_finally failed: %s", self, e)
            raise

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_request(self, request: Request, context: Context) -> Request:
        return request

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_response(self, response: Response, context: Context) -> Response:
        return response

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_exception(self, exception: Exception, context: Context) -> Response:
        raise exception

    def process_finally(self, context: Context) -> None:
        pass

    def __str__(self):
        return "<{}>".format(self.__class__.__name__)

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


def apply_middlewares(method: callable, *middlewares: Tuple[BaseProxyMiddleware]) -> callable:
    for middleware in reversed(middlewares):  # type: BaseProxyMiddleware
        method = middleware.apply(method)
    return method
