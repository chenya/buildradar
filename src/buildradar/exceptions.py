from dataclasses import dataclass, field


@dataclass
class AppError(Exception):
    message: str
    code: str = "internal_error"
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class LlmClientNotInitialisedError(AppError):
    code: str = "llm_client_not_initialised"
