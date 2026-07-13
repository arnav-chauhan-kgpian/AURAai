"""Top-level API router.

Aggregates the versioned endpoint routers into a single router mounted by the
application factory under the configured API prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, health, history, privacy, skin, upload, vto

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(skin.router, prefix="/skin", tags=["skin"])
api_router.include_router(vto.router, prefix="/vto", tags=["vto"])
api_router.include_router(upload.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
