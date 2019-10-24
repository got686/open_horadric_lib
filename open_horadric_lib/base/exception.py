from __future__ import annotations

from typing import Dict


class BaseHoradricError(Exception):
    """
    Base error for Horadric projects
    """

    text_code: str = None
    error_template: str = None

    def __init_subclass__(cls, **kwargs):
        if cls.text_code is None:
            raise ValueError("`text_code` must be set")

        if cls.error_template is None:
            raise ValueError("`error_template must be set`")

    def __init__(self, **kwargs):
        """
        Only kwargs because templating
        """
        self.kwargs: dict = kwargs

    def __str__(self):
        return self.error_template.format(**self.kwargs)


class BaseLogicError(BaseHoradricError):
    # TODO: remove checks for base errors
    text_code: str = "logic_error"
    error_template: str = "Some logic error"


class BaseHttpError(BaseHoradricError):
    text_code: str = "http_error"
    error_template: str = "Some http error"
    code: int = 500


class NotModified(BaseHttpError):
    code = 304
    text_code = "not_modified"
    error_template = "Not Modified"


class BadRequestFormat(BaseHttpError):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/415
    code = 415
    text_code = "bad_request_format"
    error_template = "Bad request mimetype: {format_}"

    def __init__(self, format_):
        # type: (str) -> None
        super(BadRequestFormat, self).__init__(format_=format_)


class RequestParsingError(BaseHttpError):
    code = 400
    text_code = "request_parsing_error"
    error_template = "Request parsing error for format: {format_}"

    def __init__(self, format_):
        # type: (str) -> None
        super(RequestParsingError, self).__init__(format_=format_)


class BadResponseFormat(BaseHttpError):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/406
    code = 406
    text_code = "bad_response_format"
    error_template = "Bad response format: {format_}"

    def __init__(self, format_):
        # type: (str) -> None
        super(BadResponseFormat, self).__init__(format_=format_)


class RequestValidationError(BaseHttpError):
    code = 400
    text_code = "request_validation_error"
    error_template = "Request validation errors: {errors}"

    def __init__(self, errors: Dict[str, str]) -> None:
        super(RequestValidationError, self).__init__(errors=errors)
