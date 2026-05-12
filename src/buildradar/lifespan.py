from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from anthropic import AsyncAnthropic
from fastapi import FastAPI

from .config import get_settings

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    settings = get_settings()
    log = logger.bind(env=settings.env)

    log.info("startup.begin")
    app.state.llm_client = (
        AsyncAnthropic(api_key=settings.anthropic_api_key.get_secret_value())
        if settings.anthropic_api_key
        else None
    )
    log.info("startup.complete")

    yield

    log.info("shutdown.begin")
    if app.state.llm_client is not None:
        await app.state.llm_client.close()
    log.info("shutdown.complete")
