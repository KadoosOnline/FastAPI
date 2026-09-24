"""Client-side exceptions.

Callers of the client catch *these*, never raw `httpx` exceptions or status
codes. This is the "error mapping" layer between HTTP and Python.
"""

from typing import Any

import httpx


class ApiError(Exception):
    """The API answered with an error status code."""

    def __init__(
        self, status_code: int, detail: Any, code: str | None = None, *, method: str, url: str
    ) -> None:
        super().__init__(f'{method} {url} -> {status_code}: {detail}')
        self.status_code = status_code
        self.detail = detail
        self.code = code


class ValidationFailed(ApiError):
    """422: the request data was rejected. `errors` holds FastAPI's error list."""

    @property
    def errors(self) -> list[dict[str, Any]]:
        return self.detail if isinstance(self.detail, list) else []


class AuthenticationFailed(ApiError):
    """401: missing, invalid or expired token, or wrong credentials."""


class PermissionDenied(ApiError):
    """403: authenticated, but not allowed."""


class NotFound(ApiError):
    """404"""


class ConflictError(ApiError):
    """409: duplicate email, course full, already enrolled, ..."""


class ServerError(ApiError):
    """5xx: a bug or outage on the server side. Usually worth a retry."""


class ApiConnectionError(Exception):
    """The request never got an HTTP answer: connection refused, DNS, timeout."""


_STATUS_TO_ERROR: dict[int, type[ApiError]] = {
    401: AuthenticationFailed,
    403: PermissionDenied,
    404: NotFound,
    409: ConflictError,
    422: ValidationFailed,
}


def error_from_response(response: httpx.Response) -> ApiError:
    """Build the most specific `ApiError` subclass for an error response."""
    try:
        body = response.json()
    except ValueError:
        body = {'detail': response.text or response.reason_phrase}
    detail = body.get('detail', body) if isinstance(body, dict) else body
    code = body.get('code') if isinstance(body, dict) else None
    status = response.status_code
    error_class = _STATUS_TO_ERROR.get(status, ServerError if status >= 500 else ApiError)
    return error_class(
        status, detail, code, method=response.request.method, url=str(response.request.url)
    )
