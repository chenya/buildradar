# src/yourapp/exception_handlers.py
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .exceptions import AppError, ErrorDetail, ErrorResponse, LLMError

_EXCEPTION_TO_STATUS_MAP: dict[type[AppError], int] = {
    AppError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    LLMError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


def _build_error_response(exc: AppError, status_code: int) -> JSONResponse:
    """Serialize an AppError subclass into a JSONResponse."""
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=ErrorDetail.from_app_error(exc)
        ).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all application exception handlers."""

    @app.exception_handler(LLMError)
    async def llm_error_handler(
        request: Request,
        exc: LLMError,
    ) -> JSONResponse:
        return _build_error_response(exc, _EXCEPTION_TO_STATUS_MAP[LLMError])

    @app.exception_handler(AppError)
    async def app_error_handler(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        return _build_error_response(exc, _EXCEPTION_TO_STATUS_MAP[AppError])
