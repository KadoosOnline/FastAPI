"""Business errors, and the ONE place where they become HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class AppError(Exception):
    status_code = 400
    code = 'app_error'

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = 'not_found'


class ConflictError(AppError):
    status_code = 409
    code = 'conflict'


class AuthenticationError(AppError):
    status_code = 401
    code = 'not_authenticated'


class PermissionDeniedError(AppError):
    status_code = 403
    code = 'permission_denied'


class FileValidationError(AppError):
    status_code = 415
    code = 'unsupported_file'


class FileTooLargeError(AppError):
    status_code = 413
    code = 'file_too_large'


class BusinessRuleError(AppError):
    status_code = 400
    code = 'business_rule'


def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    # 401 answers must say which authentication scheme the API expects.
    headers = {'WWW-Authenticate': 'Bearer'} if error.status_code == 401 else None
    return JSONResponse(
        status_code=error.status_code,
        content={'detail': error.message, 'code': error.code},
        headers=headers,
    )


def handle_integrity_error(request: Request, error: IntegrityError) -> JSONResponse:
    """Safety net: a database constraint that the service did not check first."""
    return JSONResponse(
        status_code=409, content={'detail': 'Conflicts with existing data', 'code': 'conflict'}
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)  # type: ignore[arg-type]
    app.add_exception_handler(IntegrityError, handle_integrity_error)  # type: ignore[arg-type]
