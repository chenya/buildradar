from typing import Annotated

from anthropic import AsyncAnthropic
from fastapi import Depends, Request

from .config import Settings, get_settings


def get_llm_client(request: Request) -> AsyncAnthropic | None:
    """
    Returns the AsyncAnthropic client initialised during lifespan().
    Returns None if ANTHROPIC_API_KEY was not set at startup.
    Inject via Depends() — never instantiate directly in route handlers.
    """
    return request.app.state.llm_client


def get_settings_dep() -> Settings:
    return get_settings()


# Annotated aliases — use these in route handler signatures
LLMClient = Annotated[AsyncAnthropic | None, Depends(get_llm_client)]
AppSettings = Annotated[Settings, Depends(get_settings_dep)]
