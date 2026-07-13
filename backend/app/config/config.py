"""Application configuration.

Centralised, strongly-typed settings loaded from environment variables using
Pydantic Settings. This is the single source of truth for runtime configuration
and is consumed everywhere via the cached ``get_settings`` accessor.
"""

import json
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _parse_str_list(value: object) -> object:
    """Parse a list-of-strings setting tolerantly from an env var.

    Accepts a JSON array (``["a","b"]``), a comma-separated string (``a,b``), a
    single bare value (``https://app``), or empty. This avoids a hard crash when
    a platform env var isn't strict JSON — a very common deployment foot-gun for
    ``CORS_ORIGINS`` and ``CLERK_AUTHORIZED_PARTIES``.
    """

    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
        return [part.strip() for part in text.split(",") if part.strip()]
    return value


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
    # NoDecode: parse the raw env string ourselves (see _parse_str_list) instead
    # of letting pydantic-settings require strict JSON.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

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

    # --- LLM provider -----------------------------------------------------
    # "auto" prefers Groq when a key is set, otherwise Gemini.
    llm_provider: Literal["auto", "groq", "gemini"] = "auto"

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    # A smaller/faster model for the frequent, low-stakes calls (intent
    # classification + reply summary). Big model stays for recommendations.
    groq_fast_model: str = "llama-3.1-8b-instant"
    # Cap output tokens and limit concurrent Groq calls to live within a
    # constrained TPM (tokens-per-minute) tier without 429 storms.
    groq_max_tokens: int = 1024
    groq_max_concurrency: int = 2

    # Google Gemini
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

    # --- Authentication (Clerk) ------------------------------------------
    # When False (dev/demo), unauthenticated requests fall back to an
    # anonymous context. Production must set this True.
    auth_required: bool = False
    clerk_publishable_key: str = ""
    clerk_secret_key: str = ""
    # Issuer, e.g. https://<slug>.clerk.accounts.dev ; JWKS is derived from it.
    clerk_issuer: str = ""
    clerk_jwks_url: str = ""
    # Authorized parties (`azp`) — your frontend origins.
    clerk_authorized_parties: Annotated[list[str], NoDecode] = Field(default_factory=list)
    jwks_cache_seconds: int = 600

    # --- Security ---------------------------------------------------------
    security_headers_enabled: bool = True
    hsts_enabled: bool = False  # enable only behind HTTPS
    max_upload_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_image_types: tuple[str, ...] = ("image/jpeg", "image/png", "image/webp")
    rate_limit_per_minute: int = 60
    rate_limit_enabled: bool = True
    # Per-user daily cap on chat turns (protects free-tier upstream quotas).
    # 0 disables the daily quota.
    daily_user_quota: int = 100
    virus_scan_enabled: bool = False
    clamav_host: str = ""
    clamav_port: int = 3310

    # --- Privacy / storage ------------------------------------------------
    signed_url_ttl_seconds: int = 3600
    image_retention_days: int = 30
    consent_required: bool = True
    # In-process retention sweeper (purges storage objects past the window).
    retention_sweep_enabled: bool = True
    retention_sweep_interval_hours: int = 24

    # --- Observability ----------------------------------------------------
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1
    otel_exporter_otlp_endpoint: str = ""
    otel_service_name: str = "aura-backend"
    metrics_enabled: bool = True
    # In production, /metrics is only exposed when this token is set, and the
    # caller must present it (Bearer or ?token=). Prevents public scraping of
    # operational metrics. In non-production it's open for convenience.
    metrics_token: str = ""

    @field_validator("cors_origins", "clerk_authorized_parties", mode="before")
    @classmethod
    def _coerce_str_list(cls, value: object) -> object:
        return _parse_str_list(value)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_clerk_jwks_url(self) -> str:
        """JWKS URL: explicit override, else derived from the issuer."""

        if self.clerk_jwks_url:
            return self.clerk_jwks_url
        if self.clerk_issuer:
            return f"{self.clerk_issuer.rstrip('/')}/.well-known/jwks.json"
        return ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_llm_provider(self) -> str:
        """Which LLM backend to use: 'groq', 'gemini', or 'none'."""

        if self.llm_provider != "auto":
            return self.llm_provider
        if self.groq_api_key:
            return "groq"
        if self.gemini_api_key:
            return "gemini"
        return "none"

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
