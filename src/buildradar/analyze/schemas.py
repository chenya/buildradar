# from typing import Literal


from pydantic import BaseModel, Field


class TestSummaryResponse(BaseModel):
    passed: int
    failed: int
    skipped: int


class AnalysisData(BaseModel):
    """Shared fields between AnalyzeResponse and DiagnoseRequest."""

    analysis_id: str = Field(
        description="UUID returned by /analyze — used to correlate logs"
    )
    format: str = Field(description="Detected log format")
    errors: list[str] = Field(
        description="Structured error entries from logmill"
    )
    warnings: list[str] = Field(
        description="Structured warning entries from logmill"
    )
    severity_score: int = Field(
        ge=0, le=100, description="0-100 composite severity score from logmill"
    )
    outcome: str | None = Field(
        default=None,
        description="Build outcome: Success, Failure, Unstable, Aborted",
    )
    test_summary: TestSummaryResponse | None = Field(
        default=None,
        description="Test pass/fail/skip counts; null if no tests found",
    )
    duration_seconds: float | None = Field(
        default=None,
        description="Build duration in seconds; null if no timestamps found",
    )


class AnalyzeResponse(AnalysisData):
    """Returned by POST /api/v1/analyze."""

    analyzed_at: str = Field(description="ISO 8601 UTC timestamp")
