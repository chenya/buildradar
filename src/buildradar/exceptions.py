from dataclasses import dataclass, field
from typing import Self

from pydantic import BaseModel


@dataclass
class AppError(Exception):
    message: str
    code: str = "internal_error"
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class LLMError(AppError):
    code: str = "llm_unavailable"


# Serialization schema — separate Pydantic model
class ErrorDetail(BaseModel):
    message: str
    code: str
    details: dict[str, object] = {}

    @classmethod
    def from_app_error(cls, error: AppError) -> Self:
        return cls(
            message=error.message,
            code=error.code,
            details=error.details,
        )


class ErrorResponse(BaseModel):
    error: ErrorDetail
