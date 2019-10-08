from google.protobuf.message import Message
from open_horadric_lib.base.context import Context
from open_horadric_lib.server.middleware.base import BaseServerMiddleware


class LoggingServerMiddleware(BaseServerMiddleware):
    def process_request(self, request: Message, context: Context) -> Message:
        self.logger.info("Server request: \n%s", request)
        return request

    def process_response(self, response: Message, request: Message, context: Context) -> Message:
        self.logger.info("Server response: \n%s", response)
        return response

    def process_exception(self, exception: Exception, context: Context) -> Message:
        self.logger.exception("Unknown error occurres")
        raise exception
