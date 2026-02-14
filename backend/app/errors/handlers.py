from __future__ import annotations

from typing import cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound, ProgrammingError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import (
    AppError,
    AuthError,
    ConflictError,
    InternalError,
    NotFoundError,
    PermissionError,
    ValidationError,
    error_payload,
    resolve_error_code,
)
from app.errors.types import DomainError


def register_exception_handlers(app: FastAPI, logger) -> None:
    safe_http_messages: dict[int, str] = {
        status.HTTP_400_BAD_REQUEST: ValidationError.message,
        status.HTTP_401_UNAUTHORIZED: AuthError.message,
        status.HTTP_403_FORBIDDEN: PermissionError.message,
        status.HTTP_404_NOT_FOUND: NotFoundError.message,
        status.HTTP_409_CONFLICT: ConflictError.message,
        status.HTTP_422_UNPROCESSABLE_ENTITY: ValidationError.message,
    }

    def _log_error(request: Request, status_code: int, code: str, message: str, exc: Exception | None = None) -> None:
        request_id = request.headers.get("x-request-id")
        log_message = f"[{code}] path={request.url.path} request_id={request_id or 'n/a'} message={message}"
        if status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(log_message, exc_info=exc)
        else:
            logger.warning(log_message, exc_info=exc)

    def _ensure_canonical_error_format(detail: object) -> dict[str, object] | None:
        if not isinstance(detail, dict):
            return None
        error = detail.get("error")
        if not isinstance(error, dict):
            return None
        if not isinstance(error.get("code"), str) or not isinstance(error.get("message"), str):
            return None
        return {
            "error": {
                "code": error["code"],
                "message": error["message"],
                "details": error.get("details"),
            }
        }

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        _log_error(request, exc.status_code, exc.code, exc.message, exc)
        return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, exc.message, exc.details))

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        _log_error(request, exc.status_code, exc.code, exc.message, exc)
        return JSONResponse(status_code=exc.status_code, content=error_payload(exc.code, exc.message, exc.details))

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        payload = _ensure_canonical_error_format(exc.detail)
        if payload is not None:
            error = cast(dict[str, str], payload["error"])
            _log_error(request, exc.status_code, error["code"], error["message"])
            return JSONResponse(status_code=exc.status_code, content=payload)

        safe_message = safe_http_messages.get(
            exc.status_code,
            InternalError.message if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR else "Request failed",
        )
        detail = exc.detail
        detail_message = detail if isinstance(detail, str) else ""
        log_message = detail_message.strip() or safe_message
        code = resolve_error_code(exc.status_code)
        _log_error(request, exc.status_code, code, log_message)
        return JSONResponse(status_code=exc.status_code, content=error_payload(code, safe_message, detail))

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        message = "Request validation failed"
        _log_error(request, status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError.code, message, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_payload(ValidationError.code, message, exc.errors()),
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
        log_message = str(exc).strip() or "Invalid request"
        _log_error(request, status.HTTP_400_BAD_REQUEST, ValidationError.code, log_message, exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_payload(ValidationError.code, "Invalid request", None),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        message = "Request could not be completed due to a conflict"
        _log_error(request, status.HTTP_409_CONFLICT, ConflictError.code, message, exc)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=error_payload(ConflictError.code, message, None))

    @app.exception_handler(ProgrammingError)
    async def handle_programming_error(request: Request, exc: ProgrammingError) -> JSONResponse:
        message = "Database not initialized. Ensure migrations are applied."
        _log_error(request, status.HTTP_500_INTERNAL_SERVER_ERROR, InternalError.code, message, exc)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_payload(InternalError.code, message, None))

    @app.exception_handler(NoResultFound)
    async def handle_no_result_found(request: Request, exc: NoResultFound) -> JSONResponse:
        message = "Requested resource was not found"
        _log_error(request, status.HTTP_404_NOT_FOUND, NotFoundError.code, message, exc)
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=error_payload(NotFoundError.code, message, None))

    @app.exception_handler(MultipleResultsFound)
    async def handle_multiple_results_found(request: Request, exc: MultipleResultsFound) -> JSONResponse:
        message = "Multiple resources found where one expected"
        _log_error(request, status.HTTP_409_CONFLICT, ConflictError.code, message, exc)
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=error_payload(ConflictError.code, message, None))

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        _log_error(request, status.HTTP_500_INTERNAL_SERVER_ERROR, InternalError.code, InternalError.message, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_payload(InternalError.code, InternalError.message, None),
        )
