from __future__ import annotations

import logging
from functools import wraps
from typing import Callable
from typing import Optional
from typing import Tuple
from typing import TypeVar

from google.protobuf.message import Message

from flask.wrappers import Request as FlaskRequest
from flask.wrappers import Response

Request = TypeVar("Request", FlaskRequest, Message)


class BaseProxyMiddleware(object):
    logger = logging.getLogger("proxy.middleware")

    def apply(self, method):
        @wraps(method)
        def _wrapped(request, *args, **kwargs):
            # type: (Request, tuple, dict) -> Callable[[Request, tuple, dict], Response]
            try:
                request = self._process_request(request)
                response = method(request=request, *args, **kwargs)

                return self._process_response(response)

            except Exception as exception:
                return self._process_exception(exception)

            finally:
                self._process_finally()

        return _wrapped

    def _process_request(self, request):
        # type: (Request) -> Request
        self.logger.debug("%s.process_request", repr(self))
        try:
            return self.process_request(request)
        except Exception as e:
            self.logger.exception("%s: process_request failed: %s", self, e)
            raise

    def _process_response(self, response):
        # type: (Response) -> Optional[Response]
        self.logger.debug("%s.process_response", repr(self))
        try:
            return self.process_response(response)
        except Exception as e:
            self.logger.exception("%s: process_response failed: %s", self, e)
            raise

    def _process_exception(self, exception):
        # type: (Exception) -> Optional[Response]
        self.logger.debug("%s.process_exception", repr(self))
        try:
            return self.process_exception(exception)
        except Exception as e:
            if e is not exception:
                self.logger.exception("%s: process_exception failed: %s", self, e)
            raise

    def _process_finally(self):
        # type: () -> None
        self.logger.debug("%s.process_finally", repr(self))
        try:
            return self.process_finally()
        except Exception as e:
            self.logger.exception("%s: process_finally failed: %s", self, e)
            raise

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_request(self, request):
        # type: (Request) -> Request
        return request

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_response(self, response):
        # type: (Response) -> Response
        return response

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def process_exception(self, exception):
        # type: (Exception) -> Response
        raise exception

    def process_finally(self):
        pass

    def __str__(self):
        return "<{}>".format(self.__class__.__name__)

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)


def apply_middlewares(method, *middlewares):
    # type: (callable, Tuple[BaseProxyMiddleware]) -> callable
    for middleware in reversed(middlewares):
        method = middleware.apply(method)
    return method
