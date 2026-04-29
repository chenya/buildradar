"""Main application entry point and lifespan management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from anthropic import AsyncAnthropic
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .config import get_settings
from .exceptions import (
    AppError,
    ErrorDetail,
    ErrorResponse,
    LLMError,
)
from .health.router import health_router

logger = structlog.get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        error_response = ErrorResponse(
            error=ErrorDetail.from_app_error(exc)
        ).model_dump()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )

    @app.exception_handler(LLMError)
    async def llm_client_not_initialised_handler(
        request: Request,
        exc: LLMError,
    ) -> JSONResponse:
        error_response = ErrorResponse(
            error=ErrorDetail.from_app_error(exc)
        ).model_dump()

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response,
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    log = logger.bind(env=settings.env)

    log.info("startup.begin")
    # Initialise LLM client at startup — stored on app.state
    if settings.anthropic_api_key:
        app.state.llm_client = AsyncAnthropic(
            api_key=settings.anthropic_api_key.get_secret_value()
        )
    else:
        app.state.llm_client = None  # /diagnose will return 503
    log.info("startup.complete")

    yield

    log.info("shutdown.begin")
    # Shutdown — close the client cleanly
    if app.state.llm_client is not None:
        await app.state.llm_client.close()

    log.info("shutdown.complete")


def create_app() -> FastAPI:
    settings = get_settings()
    """Factory function to create the FastAPI application instance."""
    app = FastAPI(
        title="Buildradar",
        version="1.0.0",
        docs_url="/docs" if settings.env != "production" else None,
        redoc_url="/redoc" if settings.env != "production" else None,
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.include_router(health_router, prefix="", tags=["health"])
    return app


app = create_app()
