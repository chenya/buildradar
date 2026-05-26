from fastapi import APIRouter, UploadFile, status

from ..dependencies import AppSettings
from ..exceptions import UploadFileEmptyError, UploadFileTooLargeError
from .schemas import LogAnalysisResponse
from .service import AnalyzeService

analyze_router = APIRouter(prefix="/analyze", tags=["analyze"])


@analyze_router.post(
    "/",
    response_model=LogAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_log(upload_file: UploadFile, app_settings: AppSettings):

    if upload_file.size is None or upload_file.size == 0:
        raise UploadFileEmptyError(message="Upload file is empty")

    if upload_file.size > app_settings.max_file_size_bytes:
        raise UploadFileTooLargeError(message="Upload file is too large")

    raw = await upload_file.read()

    return await AnalyzeService().analyze(raw.decode("utf-8"))
