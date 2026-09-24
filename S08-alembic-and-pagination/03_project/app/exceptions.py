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


class BusinessRuleError(AppError):
    status_code = 400
    code = 'business_rule'


def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code, content={'detail': error.message, 'code': error.code}
    )


def handle_integrity_error(request: Request, error: IntegrityError) -> JSONResponse:
    """Safety net: a database constraint that the service did not check first."""
    return JSONResponse(
        status_code=409, content={'detail': 'Conflicts with existing data', 'code': 'conflict'}
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)  # type: ignore[arg-type]
    app.add_exception_handler(IntegrityError, handle_integrity_error)  # type: ignore[arg-type]
