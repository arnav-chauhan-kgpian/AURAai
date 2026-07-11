"""FastAPI dependency providers and agent assembly.

Shared, pooled clients (YouCam, Redis) and the fully-assembled :class:`AuraAgent`
are created once at application startup and stored on ``app.state``; providers
here read them so every request reuses the same instances. ``build_aura_agent``
is the single composition root for the agent and its collaborators.
"""

from typing import Annotated, Any

from fastapi import Depends, Request

from app.agents.agent import AuraAgent
from app.agents.llm import ChatLLM
from app.agents.memory import (
    ConversationMemory,
    InMemoryProfileRepository,
    ProfileRepository,
)
from app.agents.planner import Planner
from app.agents.stores import RedisSessionCache, SupabaseProfileRepository
from app.agents.summarizer import Summarizer
from app.agents.tool_registry import ToolRegistry
from app.config.config import Settings, get_settings
from app.core.exceptions import ConfigurationError
from app.db.redis import RedisClient
from app.services.color_service import ColorService
from app.services.recommendation_service import RecommendationService
from app.services.skin_service import SkinService
from app.services.upload_service import UploadService
from app.services.vto_service import VirtualTryOnService
from app.services.youcam_client import YouCamClient
from app.tools.color_tool import ColorPaletteTool
from app.tools.memory_tool import ConversationMemoryTool
from app.tools.recommendation_tool import RecommendationTool
from app.tools.skin_tool import SkinAnalysisTool
from app.tools.vto_tool import VirtualTryOnTool

SettingsDep = Annotated[Settings, Depends(get_settings)]


# --- Shared client providers ----------------------------------------------


def get_youcam_client(request: Request) -> YouCamClient:
    """Return the shared, application-scoped YouCam client."""

    return request.app.state.youcam_client


YouCamClientDep = Annotated[YouCamClient, Depends(get_youcam_client)]


def get_upload_service(settings: SettingsDep, client: YouCamClientDep) -> UploadService:
    """Return the YouCam File API upload service."""

    return UploadService(settings, client)


UploadServiceDep = Annotated[UploadService, Depends(get_upload_service)]


def get_skin_service(
    settings: SettingsDep, client: YouCamClientDep, uploads: UploadServiceDep
) -> SkinService:
    """Return the skin analysis service."""

    return SkinService(settings, client, uploads)


def get_vto_service(
    settings: SettingsDep, client: YouCamClientDep, uploads: UploadServiceDep
) -> VirtualTryOnService:
    """Return the virtual try-on service."""

    return VirtualTryOnService(settings, client, uploads)


SkinServiceDep = Annotated[SkinService, Depends(get_skin_service)]
VirtualTryOnServiceDep = Annotated[VirtualTryOnService, Depends(get_vto_service)]


# --- Agent composition root ------------------------------------------------


def build_aura_agent(
    settings: Settings,
    *,
    youcam_client: YouCamClient,
    llm: ChatLLM,
    redis: RedisClient | None = None,
    supabase: Any | None = None,
) -> AuraAgent:
    """Compose the AuraAgent with all of its collaborators.

    This is the one place the agent's object graph is assembled — used at startup
    for the app and directly in tests with fakes.
    """

    uploads = UploadService(settings, youcam_client)
    skin_service = SkinService(settings, youcam_client, uploads)
    vto_service = VirtualTryOnService(settings, youcam_client, uploads)
    color_service = ColorService()
    recommendation_service = RecommendationService(settings, llm)

    registry = ToolRegistry(
        [
            SkinAnalysisTool(skin_service),
            VirtualTryOnTool(vto_service),
            ColorPaletteTool(color_service),
            RecommendationTool(recommendation_service),
        ]
    )

    if redis is not None:
        session_cache: Any = RedisSessionCache(redis)
    else:
        from app.agents.memory import InMemorySessionCache

        session_cache = InMemorySessionCache()
    profiles: ProfileRepository = (
        SupabaseProfileRepository(supabase) if supabase is not None else InMemoryProfileRepository()
    )
    memory = ConversationMemory(session_cache, profiles, ttl_seconds=settings.redis_ttl_seconds)

    return AuraAgent(
        settings=settings,
        planner=Planner(llm),
        registry=registry,
        memory_tool=ConversationMemoryTool(memory),
        summarizer=Summarizer(llm),
    )


def get_aura_agent(request: Request) -> AuraAgent:
    """Return the shared AuraAgent, or fail clearly if it is not configured."""

    agent = getattr(request.app.state, "aura_agent", None)
    if agent is None:
        raise ConfigurationError(
            "The AI agent is unavailable. Set GEMINI_API_KEY to enable it."
        )
    return agent


AuraAgentDep = Annotated[AuraAgent, Depends(get_aura_agent)]
