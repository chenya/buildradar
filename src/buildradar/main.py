"""Main application entry point and lifespan management."""

import structlog
from fastapi import FastAPI

from .analyze.router import analyze_router
from .config import get_settings
from .exception_handlers import register_exception_handlers
from .health.router import health_router
from .lifespan import lifespan

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()
    app = FastAPI(
        title="Buildradar",
        version="1.0.0",
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.include_router(health_router, prefix="", tags=["health"])
    app.include_router(
        analyze_router, prefix=settings.api_v1_prefix, tags=["analyze"]
    )
    return app


app = create_app()
