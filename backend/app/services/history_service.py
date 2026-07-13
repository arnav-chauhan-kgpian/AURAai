"""Turn persistence and history retrieval.

After each authenticated turn, the rich artifacts the agent produced (skin
scores, try-on outputs, recommendations) and the conversation itself are written
to Supabase so the user has a durable, per-user history. Uploaded images are
stored in object storage (biometric pixels never live in the relational tables —
only a storage key). Every write is best-effort: persistence must never break or
slow a chat response, so callers run it as a background task and failures are
logged, not raised.

In local/degraded mode (no Supabase) or for anonymous callers this is a no-op.
"""

from __future__ import annotations

from typing import Any

from app.auth.context import RequestContext
from app.core.logging import get_logger
from app.db.repositories import (
    ConversationRepository,
    RecommendationRepository,
    ScanRepository,
    TryOnRepository,
)
from app.schemas.agent import AgentImages
from app.schemas.chat import ChatResponse
from app.storage.object_store import ObjectStore

logger = get_logger(__name__)


class HistoryService:
    """Persist completed turns and read back a user's history."""

    def __init__(self, supabase: Any | None, object_store: ObjectStore | None) -> None:
        self._enabled = supabase is not None
        self._store = object_store
        if supabase is not None:
            self._conversations = ConversationRepository(supabase)
            self._scans = ScanRepository(supabase)
            self._tryons = TryOnRepository(supabase)
            self._recs = RecommendationRepository(supabase)

    @property
    def enabled(self) -> bool:
        return self._enabled

    # --- Persistence ------------------------------------------------------

    async def persist_turn(
        self,
        ctx: RequestContext,
        *,
        message: str,
        response: ChatResponse,
        images: AgentImages,
    ) -> None:
        """Best-effort write of a completed turn. Never raises."""

        if not self._enabled or ctx.is_anonymous:
            return
        try:
            await self._persist(ctx, message=message, response=response, images=images)
        except Exception as exc:  # noqa: BLE001 - persistence must never break chat
            logger.warning("history.persist_failed", session_id=ctx.session_id, error=str(exc))

    async def _persist(
        self,
        ctx: RequestContext,
        *,
        message: str,
        response: ChatResponse,
        images: AgentImages,
    ) -> None:
        base = {"user_id": ctx.user_id, "org_id": ctx.org_id, "session_id": ctx.session_id}

        await self._conversations.add(role="user", content=message, **base)
        if response.reply:
            await self._conversations.add(role="assistant", content=response.reply, **base)

        if response.skin_analysis is not None:
            image_key = await self._store_image(ctx, "face", images.face_image, "image/jpeg")
            await self._scans.create(
                {
                    **base,
                    "image_key": image_key,
                    "task_id": response.skin_analysis.task_id,
                    "scores": [s.model_dump() for s in response.skin_analysis.scores],
                    # Store only concern labels, not the heavy base64 mask URIs.
                    "overlays": [{"concern": o.concern} for o in response.skin_analysis.overlays],
                }
            )

        if response.try_on is not None:
            person_key = await self._store_image(ctx, "person", images.face_image, "image/jpeg")
            garment_key = await self._store_image(
                ctx, "garment", images.garment_image, "image/jpeg"
            )
            await self._tryons.create(
                {
                    **base,
                    "person_image_key": person_key,
                    "garment_image_key": garment_key,
                    "task_id": response.try_on.task_id,
                    "status": "completed" if response.try_on.output_images else "empty",
                    "output_images": response.try_on.output_images,
                }
            )

        if response.recommendations is not None:
            await self._recs.create({**base, "payload": response.recommendations.model_dump()})

        logger.info("history.persisted", session_id=ctx.session_id, intent=response.intent)

    async def _store_image(
        self, ctx: RequestContext, kind: str, content: bytes | None, content_type: str
    ) -> str | None:
        if content is None or self._store is None:
            return None
        key = f"{ctx.user_id}/{ctx.session_id}/{kind}-{len(content)}.jpg"
        try:
            return await self._store.put(key, content, content_type)
        except Exception as exc:  # noqa: BLE001 - image storage is best-effort
            logger.warning("history.store_image_failed", kind=kind, error=str(exc))
            return None

    # --- Retrieval --------------------------------------------------------

    async def fetch_history(self, ctx: RequestContext) -> dict[str, Any]:
        """Return the caller's recent scans, try-ons and recommendations."""

        if not self._enabled or ctx.is_anonymous:
            return {"scans": [], "try_ons": [], "recommendations": []}
        return {
            "scans": await self._scans.list_for_user(ctx.user_id),
            "try_ons": await self._tryons.list_for_user(ctx.user_id),
            "recommendations": await self._recs.list_for_user(ctx.user_id),
        }
