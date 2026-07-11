"""Startup secrets validation.

Fails fast in production if required secrets are missing or left at insecure
defaults, so a misconfigured deployment never silently serves traffic with, e.g.,
authentication disabled or CORS wide open.
"""

from app.config.config import Settings
from app.core.exceptions import ConfigurationError
from app.core.logging import get_logger

logger = get_logger(__name__)


def validate_secrets(settings: Settings) -> None:
    """Validate configuration; raise :class:`ConfigurationError` in prod on gaps."""

    problems: list[str] = []

    if settings.is_production:
        if not settings.auth_required:
            problems.append("AUTH_REQUIRED must be true in production")
        if not settings.resolved_clerk_jwks_url:
            problems.append("Clerk issuer/JWKS must be configured")
        if not settings.youcam_api_key or not settings.youcam_secret_key:
            problems.append("YouCam credentials are required")
        if settings.resolved_llm_provider == "none":
            problems.append("An LLM provider key (Groq or Gemini) is required")
        if not settings.supabase_url or not settings.supabase_service_role_key:
            problems.append("Supabase credentials are required")
        if any("*" in origin for origin in settings.cors_origins):
            problems.append("CORS_ORIGINS must not contain wildcards in production")
        if not settings.hsts_enabled:
            logger.warning("secrets.hsts_disabled", note="enable HSTS behind HTTPS")

    if problems:
        for problem in problems:
            logger.error("secrets.invalid", problem=problem)
        raise ConfigurationError("; ".join(problems))

    logger.info("secrets.validated", environment=settings.environment)
