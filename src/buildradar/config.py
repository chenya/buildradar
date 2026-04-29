# src/buildradar/config.py

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All application configuration loaded and validated at startup.

    Never call os.environ.get() in route handlers or service code.
    Always inject settings via get_settings() through Depends().

    Environment variables are read from the shell environment and
    optionally from a .env file in the project root.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # ANTHROPIC_API_KEY == anthropic_api_key
        extra="ignore",  # silently ignore unknown env vars
    )

    # ── Application ──────────────────────────────────────────────────────────
    env: Literal["development", "staging", "production"] = "development"

    app_name: str = "buildradar"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    # ── Logging ──────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ── API docs ─────────────────────────────────────────────────────────────
    # Automatically disabled in production via model_validator below
    docs_enabled: bool = True

    # ── File upload ──────────────────────────────────────────────────────────
    max_file_size_mb: int = Field(default=50, ge=1, le=500)

    # ── Server ───────────────────────────────────────────────────────────────
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=1, ge=1, le=16)

    # ── Thread pool ──────────────────────────────────────────────────────────
    # Controls how many log files can be parsed concurrently
    # via asyncio.to_thread() — each parse runs in its own thread
    thread_pool_workers: int = Field(default=4, ge=1, le=32)

    # ── LLM ─────────────────────────────────────────────────────────────────
    # Optional — if absent,
    #           /diagnose returns 503 and /ready returns unavailable.
    # /analyze is fully independent and unaffected.
    anthropic_api_key: SecretStr | None = None

    # ── Computed properties ──────────────────────────────────────────────────
    @property
    def max_file_size_bytes(self) -> int:
        """Pre-computed byte limit used in the analyze router."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def docs_url(self) -> str | None:
        """Returns None in production to disable Swagger UI."""
        return None if self.is_production else "/docs"

    @property
    def redoc_url(self) -> str | None:
        """Returns None in production to disable ReDoc."""
        return None if self.is_production else "/redoc"

    @property
    def openapi_url(self) -> str | None:
        """Returns None in production to prevent schema exposure."""
        return None if self.is_production else "/openapi.json"

    # ── Validators ───────────────────────────────────────────────────────────
    @field_validator("api_v1_prefix")
    @classmethod
    def prefix_must_start_with_slash(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("api_v1_prefix must start with '/'")
        return v

    @model_validator(mode="after")
    def disable_docs_in_production(self) -> "Settings":
        """Force docs_enabled = False when env = production."""
        if self.env == "production":
            self.docs_enabled = False
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Returns the singleton Settings instance.

    Cached with @lru_cache — constructed and validated exactly once
    per process lifetime. All subsequent calls return the same instance.

    Usage in route handlers:
        from buildradar.dependencies import AppSettings
        async def my_route(settings: AppSettings): ...

    Usage in tests — override via dependency_overrides:
        app.dependency_overrides[get_settings] = lambda: Settings(env="development")
    """
    return Settings()
