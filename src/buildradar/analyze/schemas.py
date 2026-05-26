# from typing import Literal

from pydantic import BaseModel

# class RootCause(BaseModel):
#     id: int
#     summary: str
#     related_errors: list[str]
#     is_cascading: bool
#     cascading_from: str | None


# class Fix(BaseModel):
#     root_cause_id: int
#     action: str
#     rationale: str


# class Warning(BaseModel):
#     warning: str
#     risk: str


# class BuildAnalysis(BaseModel):
#     build_status: Literal["failed", "passed", "unstable"]
#     root_causes: list[RootCause]
#     fixes: list[Fix]
#     warnings_to_watch: list[Warning]
#     ambiguous: bool
#     hypotheses: list[str]
#     insufficient_info: bool
#     additional_logs_needed: list[str]
#     health_summary: str


class TestSummaryResponse(BaseModel):
    passed: int
    failed: int
    skipped: int


class LogAnalysisRequest(BaseModel):
    pass


class LogAnalysisResponse(BaseModel):
    format: str
    errors: list[str]
    warnings: list[str]
    duration_seconds: float | None
    severity_score: int
    outcome: str | None
    test_summary: TestSummaryResponse | None
