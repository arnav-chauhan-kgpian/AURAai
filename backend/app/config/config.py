"""Application configuration.

Centralised, strongly-typed settings loaded from environment variables using
Pydantic Settings. This is the single source of truth for runtime configuration
and is consumed everywhere via the cached ``get_settings`` accessor.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the AuraAI backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Application -------------------------------------------------------
    app_name: str = "AuraAI"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- Server -----------------------------------------------------------
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # --- YouCam (Perfect Corp) credentials --------------------------------
    youcam_api_key: str = ""
    # RSA public key (PEM) issued alongside the API key; used to build the
    # authentication ``id_token``.
    youcam_secret_key: str = ""
    youcam_base_url: str = "https://yce-api-01.perfectcorp.com"

    # --- YouCam endpoints (paths relative to ``youcam_base_url``) ----------
    youcam_auth_path: str = "/s2s/v1.0/client/auth"
    youcam_file_skin_path: str = "/s2s/v2.0/file/skin-analysis"
    youcam_task_skin_path: str = "/s2s/v1.0/task/skin-analysis"
    youcam_file_cloth_path: str = "/s2s/v2.0/file/cloth"
    youcam_task_cloth_path: str = "/s2s/v2.0/task/cloth"

    # --- YouCam HTTP client ------------------------------------------------
    youcam_connect_timeout_seconds: float = 10.0
    youcam_request_timeout_seconds: float = 30.0
    youcam_max_connections: int = 20
    youcam_max_keepalive_connections: int = 10
    youcam_token_ttl_seconds: int = 600

    # --- YouCam retry / backoff -------------------------------------------
    youcam_max_retries: int = 4
    youcam_retry_backoff_base_seconds: float = 0.5
    youcam_retry_backoff_max_seconds: float = 20.0
    youcam_retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504)

    # --- YouCam polling ----------------------------------------------------
    youcam_poll_interval_seconds: float = 2.0
    youcam_poll_timeout_seconds: float = 120.0

    # --- YouCam rate limiting ---------------------------------------------
    # Ceiling on concurrent in-flight requests to the provider.
    youcam_max_concurrent_requests: int = 8

    # --- Google Gemini ----------------------------------------------------
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # --- Supabase ---------------------------------------------------------
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "aura-uploads"

    # --- Redis ------------------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl_seconds: int = 3600

    # --- Agent ------------------------------------------------------------
    agent_max_iterations: int = 12
    agent_recursion_limit: int = 25

    def _youcam_url(self, path: str) -> str:
        return f"{self.youcam_base_url.rstrip('/')}{path}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def youcam_auth_url(self) -> str:
        return self._youcam_url(self.youcam_auth_path)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def youcam_file_skin_url(self) -> str:
        return self._youcam_url(self.youcam_file_skin_path)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def youcam_task_skin_url(self) -> str:
        return self._youcam_url(self.youcam_task_skin_path)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def youcam_file_cloth_url(self) -> str:
        return self._youcam_url(self.youcam_file_cloth_path)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def youcam_task_cloth_url(self) -> str:
        return self._youcam_url(self.youcam_task_cloth_path)


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached ``Settings`` instance."""

    return Settings()
