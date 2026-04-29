from fastapi import APIRouter, status

from ..dependencies import LLMClient
from ..exceptions import LLMError
from .schemas import HealthStatus, ReadyStatus

health_router = APIRouter()


@health_router.get(
    "/health", status_code=status.HTTP_200_OK, include_in_schema=False
)
async def liveness() -> HealthStatus:
    return HealthStatus(status="ok")


@health_router.get(
    "/ready", status_code=status.HTTP_200_OK, include_in_schema=False
)
async def readiness(llm_client: LLMClient) -> ReadyStatus:
    # llm_client = None
    if llm_client is None:
        raise LLMError(message="LLM client is unavailable")

    return ReadyStatus(status="ready")
