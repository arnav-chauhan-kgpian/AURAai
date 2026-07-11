"""Application entrypoint.

Builds and configures the FastAPI application: logging, middleware, exception
handlers and versioned routers. Import ``app`` from here to run under an ASGI
server (``uvicorn app.main:app``).
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config.config import get_settings
from app.core.dependencies import build_aura_agent
from app.core.logging import configure_logging, get_logger
from app.db.redis import get_redis_client
from app.db.supabase import get_supabase_client
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_context import RequestContextMiddleware
from app.services.youcam_client import YouCamClient

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown side effects.

    Shared, pooled clients (YouCam, Redis) and the assembled AuraAgent are
    created here and reused for the process lifetime, then closed on shutdown.
    The agent is only built when a Gemini key is configured; otherwise the direct
    YouCam REST endpoints still work and the chat endpoint reports it clearly.
    """

    settings = get_settings()
    app.state.youcam_client = YouCamClient(settings)
    app.state.redis = get_redis_client(settings)
    app.state.aura_agent = None

    if settings.gemini_api_key:
        from app.services.gemini_client import GeminiChatModel

        try:
            supabase = get_supabase_client(settings)
        except Exception:  # noqa: BLE001 - Supabase is optional for the agent
            supabase = None
        app.state.aura_agent = build_aura_agent(
            settings,
            youcam_client=app.state.youcam_client,
            llm=GeminiChatModel(settings),
            redis=app.state.redis,
            supabase=supabase,
        )
    else:
        logger.warning("agent.disabled", reason="GEMINI_API_KEY not set")

    logger.info("application.startup", environment=settings.environment)
    try:
        yield
    finally:
        await app.state.youcam_client.aclose()
        await app.state.redis.aclose()
        logger.info("application.shutdown")


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application instance."""

    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AuraAI — Personal Skin & Style Agent",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
