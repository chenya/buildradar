from datetime import UTC, datetime

import structlog
from anthropic import AsyncAnthropic

from ..config import Settings
from ..exceptions import LLMError
from .schemas import (
    DiagnoseRequest,
    DiagnoseResponse,
    DiagnosisResult,
)

log = structlog.get_logger()
VERSION = "1.0"
SYSTEM_PROMPT = """
<role>
You are a senior DevOps engineer and SRE with 20+ years of hands-on experience across
CI/CD platforms (Jenkins, GitHub Actions, GitLab CI, CircleCI, TeamCity, Azure DevOps,
Bamboo) and the full software delivery stack.
</role>

<expertise>
    <build_systems>Maven, Gradle, npm, pip, cargo, make</build_systems>
    <containerization>Docker, Kubernetes, Helm</containerization>
    <languages>Python, Java, Node.js, Go, Ruby, .NET, Rust, C, C++</languages>
    <infrastructure>Terraform, Ansible, AWS, GCP, Azure</infrastructure>
    <testing>JUnit, pytest, Jest, Cypress, Selenium</testing>
    <failure_domains>
        dependency resolution, environment config, flaky tests,
        resource exhaustion, network timeouts, permission errors, race conditions
    </failure_domains>
</expertise>

<diagnostic_approach>
Follow these steps in order:
1. Identify the true root cause — not just the last error, but what triggered the chain
2. Distinguish cascading failures — one upstream failure causes many downstream errors; treat as one issue
3. Assess blast radius — what is blocked or broken as a result
4. Prioritize by severity — not by order of appearance in the log
5. Propose the minimal effective fix — avoid over-engineering
6. State the blast radius — what downstream builds, deployments, or teams are blocked
</diagnostic_approach>

<reasoning_rules>
- Read error messages literally and precisely — never paraphrase or generalize them
- Consider environment context: fresh run, retry, merge, or scheduled job
- Distinguish deterministic failures (always fails) from flaky failures (intermittent)
- Flag explicitly when a fix is a workaround vs. a permanent solution
- If the log summary is insufficient to diagnose confidently, state what additional output is needed — do not guess
</reasoning_rules>

<output_rules>
- Assume the reader is a competent engineer — skip generic advice
- Lead with the diagnosis, not a preamble
- Reference actual error text, line numbers, or config keys when available
- A fix that leaves a follow-up failure unaddressed is not a complete fix
- Return only valid JSON matching the provided schema — no prose, no markdown fences
</output_rules>
"""


class DiagnoseService:
    def __init__(self, llm_client: AsyncAnthropic, settings: Settings) -> None:
        self._client = llm_client
        self._settings = settings
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens

    async def diagnose(self, request: DiagnoseRequest) -> DiagnoseResponse:
        diagnosed_at = datetime.now(UTC).isoformat()

        llm_response = await self._client.messages.parse(
            model=self._model,
            max_tokens=self._max_tokens,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": self._build_prompt(request),
                }
            ],
            output_format=DiagnosisResult,
        )

        log.info(
            "diagnose.completed",
            analysis_id=request.analysis_id,
            stop_reason=llm_response.stop_reason,
            model=llm_response.model,
        )

        if llm_response.stop_reason == "refusal":
            raise LLMError(
                message="LLM refused to diagnose this content",
                details={"analysis_id": request.analysis_id},
            )

        if llm_response.stop_reason == "max_tokens":
            raise LLMError(
                message="LLM response was truncated — increase MAX_TOKENS",
                details={
                    "analysis_id": request.analysis_id,
                    "max_tokens": self._max_tokens,
                },
            )

        return DiagnoseResponse(
            analysis_id=request.analysis_id,
            diagnosed_at=diagnosed_at,
            version=VERSION,
            ci_system=request.format,
            build_outcome=request.outcome,
            severity_score=request.severity_score,
            diagnosis=llm_response.parsed_output,
        )

    def _build_prompt(self, request: DiagnoseRequest) -> str:
        """
        Builds the user message that pairs with SYSTEM_PROMPT.
        """
        sections: list[str] = []

        # Build context
        context_lines = [
            f"CI/CD system:   {request.format}",
            f"Build outcome:  {request.outcome or 'Unknown'}",
            f"Severity score: {request.severity_score}/100",
        ]
        if request.duration_seconds is not None:
            context_lines.append(
                f"Build duration: {request.duration_seconds:.1f}s"
            )
        if request.test_summary is not None:
            t = request.test_summary
            context_lines.append(
                f"Test results:   "
                f"{t.passed} passed, {t.failed} failed, {t.skipped} skipped"
            )
        sections.append(
            "<build_context>\n"
            + "\n".join(context_lines)
            + "\n</build_context>"
        )

        # Errors
        error_lines = [
            f"{i}. {error}" for i, error in enumerate(request.errors, start=1)
        ]
        sections.append("<errors>\n" + "\n".join(error_lines) + "\n</errors>")

        # Warnings
        if request.warnings:
            warning_lines = [
                f"{i}. {warning}"
                for i, warning in enumerate(request.warnings, start=1)
            ]
            sections.append(
                "<warnings>\n" + "\n".join(warning_lines) + "\n</warnings>"
            )

        # Correlation ID
        sections.append(f"<analysis_id>{request.analysis_id}</analysis_id>")

        return "\n\n".join(sections)
