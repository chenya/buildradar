from fastapi import APIRouter, status

from ..dependencies import LLMClient
from ..exceptions import LlmClientNotInitialisedError
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
async def ready(llm_client: LLMClient) -> ReadyStatus:
    # llm_client = None
    if llm_client is None:
        raise LlmClientNotInitialisedError(
            message="LLM client not initialised"
        )
        # raise HTTPException(
        #     status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        #     detail="LLM client not initialised",
        # )

    return ReadyStatus(status="ok")
