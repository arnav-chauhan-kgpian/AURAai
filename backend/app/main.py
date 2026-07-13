"""Application entrypoint.

Builds and configures the FastAPI application: logging, security middleware,
observability, exception handlers and versioned routers. Import ``app`` from here
to run under an ASGI server (``uvicorn app.main:app``).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.auth.clerk import ClerkVerifier
from app.auth.session import AuditLogger, SessionService
from app.config.config import get_settings
from app.core.dependencies import build_aura_agent
from app.core.logging import configure_logging, get_logger
from app.db.redis import get_redis_client
from app.db.supabase import get_supabase_client
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_context import RequestContextMiddleware
from app.observability.setup import init_observability
from app.security.headers import SecurityHeadersMiddleware
from app.security.secrets import validate_secrets
from app.services.retention import RetentionScheduler
from app.services.youcam_client import YouCamClient
from app.storage.object_store import ObjectStore

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown.

    Validates secrets (fails fast in prod), builds shared clients and the agent,
    and wires auth/session/audit/storage onto ``app.state``. On shutdown, closes
    pooled clients for a graceful exit.
    """

    settings = get_settings()
    validate_secrets(settings)

    try:
        supabase = get_supabase_client(settings)
    except Exception:  # noqa: BLE001 - Supabase optional in dev
        supabase = None

    app.state.settings = settings
    app.state.supabase = supabase
    app.state.youcam_client = YouCamClient(settings)
    app.state.redis = get_redis_client(settings)
    app.state.object_store = ObjectStore(settings, supabase) if supabase is not None else None
    app.state.clerk_verifier = ClerkVerifier(settings)
    app.state.session_service = SessionService(settings, supabase)
    app.state.audit = AuditLogger(supabase)
    app.state.aura_agent = None

    from app.services.llm_factory import build_llm

    llm = build_llm(settings)
    if llm is not None:
        app.state.aura_agent = build_aura_agent(
            settings,
            youcam_client=app.state.youcam_client,
            llm=llm,
            fast_llm=build_llm(settings, fast=True),
            redis=app.state.redis,
            supabase=supabase,
        )
    else:
        logger.warning("agent.disabled", reason="no LLM provider key configured (Groq/Gemini)")

    app.state.retention = RetentionScheduler(settings, app.state.object_store)
    app.state.retention.start()

    logger.info(
        "application.startup",
        environment=settings.environment,
        auth_required=settings.auth_required,
        clerk_configured=app.state.clerk_verifier.configured,
    )
    try:
        yield
    finally:
        await app.state.retention.stop()
        await app.state.youcam_client.aclose()
        await app.state.redis.aclose()
        logger.info("application.shutdown")


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application instance."""

    configure_logging()
    settings = get_settings()

    # Disable interactive docs / schema in production to reduce surface area.
    docs_kwargs = (
        {"docs_url": None, "redoc_url": None, "openapi_url": None}
        if settings.is_production
        else {}
    )
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AuraAI — Personal Skin & Style Agent",
        debug=settings.debug,
        lifespan=lifespan,
        **docs_kwargs,
    )

    # Middleware runs in reverse registration order: request-context first
    # (correlation id), then CORS, then security headers on the way out.
    if settings.security_headers_enabled:
        app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Session-Id", "X-Request-ID"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    init_observability(app, settings)

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    # Root-level liveness/readiness aliases so platform probes and uptime checks
    # can hit /health and /ready directly (in addition to the versioned paths).
    from app.api.v1.endpoints import health

    app.include_router(health.router, include_in_schema=False)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        """Friendly service banner at the API root (avoids a bare 404)."""

        return {
            "service": "AuraAI API",
            "status": "ok",
            "health": "/health",
            "ready": "/ready",
            "api": settings.api_v1_prefix,
        }

    return app


app = create_app()
