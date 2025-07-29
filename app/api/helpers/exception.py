"""
isort:skip_file
"""
import http
from http.client import BAD_REQUEST

from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_503_SERVICE_UNAVAILABLE,
)


class DomainException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.error_code = "no_code"
        self.status_code = "no_status_code"


class CurrencyDoesNotExistException(DomainException):
    def __init__(self, message="Currency does not exist"):
        super().__init__(message)
        self.error_code = "currency_does_not_exists_error"
        self.status_code = HTTP_404_NOT_FOUND


class CurrencyAlreadyExistException(DomainException):
    def __init__(self, message="Currency already exist"):
        super().__init__(message)
        self.error_code = "currency_already_exists_error"
        self.status_code = HTTP_409_CONFLICT


class ExternalAPIUnreachableException(DomainException):
    def __init__(self, message="Cannot reach external Currency API"):
        super().__init__(message)
        self.error_code = "unavailable_external_api_error"
        self.status_code = HTTP_503_SERVICE_UNAVAILABLE


class NoCurrencyFoundException(DomainException):
    def __init__(self, message="Cannot find any currency on database"):
        super().__init__(message)
        self.error_code = "no_currency_found_error"
        self.status_code = HTTP_404_NOT_FOUND


class HTTPError(Exception):
    def __init__(
        self,
        status_code: int = None,
        error_message: str = None,
        error_code: str = None,
    ) -> None:
        if status_code is None:
            status_code = BAD_REQUEST
        if error_message is None:
            error_message = http.HTTPStatus(status_code).phrase
        if error_code is None:
            error_code = http.HTTPStatus(  # pylint: disable=E1101
                status_code,
            ).name.lower()
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = error_message

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}(status_code={self.status_code!r},"
            f"error_code={self.error_code!r},"
            f"error_message={self.error_message!r})"
        )
