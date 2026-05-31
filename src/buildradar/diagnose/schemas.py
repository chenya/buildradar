# diagnose/schemas.py
from enum import StrEnum

from pydantic import BaseModel, Field

from ..analyze.schemas import AnalysisData

# ENUMS


class SeverityLabel(StrEnum):
    CLEAN = "Clean"
    MINOR = "Minor"
    MODERATE = "Moderate"
    SERIOUS = "Serious"
    CRITICAL = "Critical"


class ErrorCategory(StrEnum):
    COMPILATION = "Compilation"
    TEST_FAILURE = "Test Failure"
    DEPENDENCY = "Dependency"
    RUNTIME = "Runtime"
    LINT = "Lint"
    ENVIRONMENT = "Environment"
    UNKNOWN = "Unknown"


class FailureType(StrEnum):
    DETERMINISTIC = "Deterministic"  # always fails - fix required
    FLAKY = "Flaky"  # intermittent - investigate further
    ENVIRONMENT = "Environment"  # infra/config issue outside the code
    UNKNOWN = "Unknown"


class Confidence(StrEnum):
    HIGH = "High"  # errors are explicit and traceable to a root cause
    MEDIUM = "Medium"  # likely cause identified but log context is partial
    LOW = "Low"  # insufficient data - further investigation required


# Nested models


class AffectedArea(BaseModel):
    category: ErrorCategory = Field(description="Error category grouping")
    files: list[str] = Field(
        description="Source files extracted from error messages"
    )
    error_count: int = Field(
        ge=0, description="Number of errors in this category"
    )
    summary: str = Field(
        description="One sentence describing what is broken in this area"
    )


class RemediationStep(BaseModel):
    order: int = Field(
        ge=1, description="Execution order - apply steps in ascending order"
    )
    action: str = Field(description="Concrete imperative action to take")
    file: str | None = Field(
        default=None, description="File to edit, if applicable"
    )
    line: int | None = Field(
        default=None, description="Line number, if extractable from the error"
    )
    rationale: str = Field(description="Why this step resolves the problem")
    is_workaround: bool = Field(
        default=False,
        description=(
            "True if this is a temporary workaround rather "
            "than a permanent fix"
        ),
    )


class DiagnosisMeta(BaseModel):
    confidence: Confidence = Field(
        description="Confidence level of the diagnosis"
    )
    failure_type: FailureType = Field(
        description=(
            "Whether the failure is deterministic, flaky, or environmental"
        )
    )
    additional_context_needed: str | None = Field(
        default=None,
        description=(
            "Set when confidence is Low. "
            "Describes exactly what additional log output or context "
            "is needed to make a confident diagnosis."
        ),
    )


# Request


class TestSummaryRequest(BaseModel):
    passed: int
    failed: int
    skipped: int


class DiagnoseRequest(AnalysisData):
    """
    Sent to POST /api/v1/diagnose.
    Identical to AnalyzeResponse without analyzed_at,
    plus any future diagnosis-specific context fields.
    """

    pass


# LLM output


class DiagnosisResult(BaseModel):
    """
    The structured payload produced by the LLM via client.messages.parse().
    This is the inner diagnosis - it does not carry HTTP metadata.
    Wrapped by DiagnoseResponse before being returned to the caller.
    """

    summary: str = Field(
        description=(
            "One sentence describing what went wrong. "
            "Lead with the failure, not a preamble. "
            "Example: TypeScript compilation failed due to a missing "
            "field on the User type, blocking the build entirely."
        )
    )
    root_cause: str = Field(
        description=(
            "The single underlying problem that triggered the failure chain. "
            "Distinguish the root cause from its symptoms. "
            "If one upstream error caused many downstream errors, "
            "name the upstream error. "
            "Reference the actual error text, file, "
            "and line number where available."
        )
    )
    severity_label: SeverityLabel = Field(
        description=(
            "Human-readable severity derived from the severity score "
            "and outcome"
        )
    )
    can_deploy: bool = Field(
        description=(
            "False when outcome is Failure or severity is Serious/Critical. "
            "True only when all issues are non-blocking warnings "
            "or minor lint findings."
        )
    )
    affected_areas: list[AffectedArea] = Field(
        description=(
            "Errors grouped by category. "
            "Each group identifies the files involved."
        )
    )
    remediation_steps: list[RemediationStep] = Field(
        description=(
            "Ordered steps to resolve the failure. "
            "Step 1 must address the root cause. "
            "Subsequent steps address cascading effects or follow-up risks. "
            "Be specific - reference file names, line numbers, "
            "and exact changes."
        )
    )
    meta: DiagnosisMeta = Field(
        description="Confidence and failure type metadata for this diagnosis"
    )
    blast_radius: str | None = Field(
        default=None,
        description=(
            "What else is blocked or affected by this failure beyond "
            "the immediate build. "
            "Null when the impact is contained to this build only."
        ),
    )


# API response


class DiagnoseResponse(BaseModel):
    """
    Professional REST API response envelope for POST /api/v1/diagnose.

    Structure:
        meta        - request tracing and timing
        request     - echoed inputs for client correlation
        diagnosis   - the structured LLM output
    """

    # Response metadata
    analysis_id: str = Field(
        description=(
            "Echoed from DiagnoseRequest - correlates with the /analyze call"
        )
    )
    diagnosed_at: str = Field(
        description=(
            "ISO 8601 UTC timestamp of when the diagnosis was produced"
        ),
    )
    version: str = Field(
        default="1.0",
        description=(
            "Diagnosis schema version - "
            "allows clients to handle future changes"
        ),
    )

    #  Request summary
    ci_system: str = Field(
        description=("CI/CD system that produced the log. example: jenkins")
    )
    build_outcome: str | None = Field(
        default=None,
        description=(
            "Build outcome as reported by the parser: "
            "Success, Failure, Unstable, Aborted"
        ),
    )
    severity_score: int = Field(
        ge=0,
        le=100,
        description=(
            "0-100 severity score from logmill, echoed for client convenience"
        ),
    )

    # The Diagnosis
    diagnosis: DiagnosisResult | None = Field(
        description="Structured diagnosis produced by the LLM"
    )
