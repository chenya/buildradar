import structlog
from fastapi import APIRouter, status

from ..dependencies import AppSettings, LLMClient
from ..exceptions import LLMError
from .schemas import DiagnoseRequest, DiagnoseResponse
from .service import DiagnoseService

log = structlog.get_logger()
diagnose_router = APIRouter(prefix="/diagnose", tags=["diagnose"])


@diagnose_router.post(
    "/",
    response_model=DiagnoseResponse,
    status_code=status.HTTP_200_OK,
    responses={
        422: {"description": "Validation error"},
        503: {"description": "LLM client error"},
    },
)
async def diagnose_log(
    request: DiagnoseRequest, llm_client: LLMClient, app_settings: AppSettings
) -> DiagnoseResponse:
    if llm_client is None:
        raise LLMError(
            message="LLM client not initialised - set ANTHROPIC_API_KEY",
            details={"analysis_id": request.analysis_id},
        )

    structlog.contextvars.bind_contextvars(analysis_id=request.analysis_id)
    log.info("diagnose.started", severity_score=request.severity_score)

    service = DiagnoseService(llm_client, app_settings)
    return await service.diagnose(request)
