from fastapi import APIRouter, UploadFile, status

from ..dependencies import AppSettings
from ..exceptions import (
    UnsupportedFormatError,
    UploadFileEmptyError,
    UploadFileTooLargeError,
)
from .schemas import AnalyzeResponse
from .service import AnalyzeService

analyze_router = APIRouter(prefix="/analyze", tags=["analyze"])


@analyze_router.post(
    "/",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        415: {
            "description": "Unsupported media type — must be multipart/form-data"
        },
        413: {"description": "Log file exceeds maximum allowed size"},
        422: {"description": "Validation error — missing file field"},
    },
)
async def analyze_log(
    upload_file: UploadFile, app_settings: AppSettings
) -> AnalyzeResponse:

    def _check_file_size(num_bytes: int) -> None:
        if num_bytes > app_settings.max_file_size_bytes:
            raise UploadFileTooLargeError(
                message=(
                    f"File exceeds maximum size of {app_settings.max_file_size_mb}MB"
                ),
                details={"max_mb": app_settings.max_file_size_mb},
            )

    def _check_file_empty(length_bytes: int) -> None:
        if length_bytes == 0:
            raise UploadFileEmptyError(
                message="Uploaded file is empty",
                details={"filename": upload_file.filename},
            )

    def _check_media_type(content_type) -> None:
        if content_type is None:
            return

        allowed_content_types = {
            "text/plain",
            "multipart/form-data",
            "application/octet-stream",
        }

        if content_type not in allowed_content_types:
            raise UnsupportedFormatError(
                message=f"{content_type} is not supported",
                details={"supported_types": list(allowed_content_types)},
            )

    # Guard 1 — support media type
    _check_media_type(upload_file.content_type)

    # Guard 2 — cheap pre-read check when Content-Length is present
    if upload_file.size is not None:
        _check_file_size(upload_file.size)

    raw = await upload_file.read()
    raw = raw.strip()

    # Guard 3 — empty file
    _check_file_empty(len(raw))

    # Guard 4 — post-read check catches chunked transfer encoding
    _check_file_size(len(raw))

    service = AnalyzeService()

    return await service.analyze(raw.decode("utf-8", errors="replace"))
