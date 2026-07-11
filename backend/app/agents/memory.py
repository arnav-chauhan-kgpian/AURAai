"""Conversation memory.

Two-tier memory for the agent:

* **Short-term** — recent conversation history and the latest skin/try-on/color
  snapshot, held in a fast session cache (Redis in production).
* **Long-term** — the user's durable profile (skin type, Fitzpatrick, favorite
  colors, preferred style), held in a profile repository (Supabase).

``ConversationMemory`` depends on two narrow backend protocols so it can be unit
tested with in-memory implementations and wired to Redis/Supabase in production
(see ``app.agents.stores``). All operations are best-effort: a memory backend
outage degrades gracefully rather than failing a chat turn.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.core.logging import get_logger
from app.schemas.chat import ChatMessage
from app.schemas.color import ColorPalette
from app.schemas.recommendation import RecommendationSet
from app.schemas.skin import SkinAnalysisResponse
from app.schemas.vto import TryOnResponse

logger = get_logger(__name__)

HISTORY_LIMIT = 20


class SessionCache(Protocol):
    """Short-term key/value + list cache (Redis-backed in production)."""

    async def read(self, key: str) -> str | None: ...
    async def write(self, key: str, value: str, ttl: int) -> None: ...
    async def append(self, key: str, value: str, ttl: int) -> None: ...
    async def read_list(self, key: str, limit: int) -> list[str]: ...


class ProfileRepository(Protocol):
    """Long-term durable profile store (Supabase-backed in production)."""

    async def fetch(self, session_id: str) -> dict[str, Any] | None: ...
    async def upsert(self, session_id: str, data: dict[str, Any]) -> None: ...


@dataclass
class MemoryContext:
    """Everything the agent recalls for a session at the start of a turn."""

    history: list[ChatMessage] = field(default_factory=list)
    profile: dict[str, Any] = field(default_factory=dict)
    snapshot: dict[str, Any] = field(default_factory=dict)

    def history_lines(self) -> list[str]:
        return [f"{m.role}: {m.content}" for m in self.history]


# --- In-memory backends (used by tests and as a safe default) --------------


class InMemorySessionCache:
    """Process-local implementation of :class:`SessionCache`."""

    def __init__(self) -> None:
        self._values: dict[str, str] = {}
        self._lists: dict[str, list[str]] = {}

    async def read(self, key: str) -> str | None:
        return self._values.get(key)

    async def write(self, key: str, value: str, ttl: int) -> None:
        self._values[key] = value

    async def append(self, key: str, value: str, ttl: int) -> None:
        self._lists.setdefault(key, []).append(value)

    async def read_list(self, key: str, limit: int) -> list[str]:
        return self._lists.get(key, [])[-limit:]


class InMemoryProfileRepository:
    """Process-local implementation of :class:`ProfileRepository`."""

    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, Any]] = {}

    async def fetch(self, session_id: str) -> dict[str, Any] | None:
        return self._profiles.get(session_id)

    async def upsert(self, session_id: str, data: dict[str, Any]) -> None:
        current = self._profiles.setdefault(session_id, {})
        current.update(data)


# --- Memory facade ---------------------------------------------------------


class ConversationMemory:
    """Coordinates short-term and long-term memory for the agent."""

    def __init__(
        self, cache: SessionCache, profiles: ProfileRepository, *, ttl_seconds: int = 3600
    ) -> None:
        self._cache = cache
        self._profiles = profiles
        self._ttl = ttl_seconds

    @staticmethod
    def _history_key(session_id: str) -> str:
        return f"aura:history:{session_id}"

    @staticmethod
    def _snapshot_key(session_id: str) -> str:
        return f"aura:snapshot:{session_id}"

    async def recall(self, session_id: str) -> MemoryContext:
        """Load history, latest snapshot and durable profile for a session."""

        try:
            raw_history = await self._cache.read_list(self._history_key(session_id), HISTORY_LIMIT)
            history = [ChatMessage.model_validate_json(item) for item in raw_history]
            raw_snapshot = await self._cache.read(self._snapshot_key(session_id))
            snapshot = json.loads(raw_snapshot) if raw_snapshot else {}
            profile = await self._profiles.fetch(session_id) or {}
            return MemoryContext(history=history, profile=profile, snapshot=snapshot)
        except Exception as exc:  # noqa: BLE001 - memory is best-effort
            logger.warning("memory.recall_failed", session_id=session_id, error=str(exc))
            return MemoryContext()

    async def append_message(self, session_id: str, message: ChatMessage) -> None:
        try:
            await self._cache.append(
                self._history_key(session_id), message.model_dump_json(), self._ttl
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("memory.append_failed", session_id=session_id, error=str(exc))

    async def persist(
        self,
        session_id: str,
        *,
        user_message: ChatMessage,
        assistant_message: ChatMessage,
        skin_analysis: SkinAnalysisResponse | None = None,
        try_on: TryOnResponse | None = None,
        color_palette: ColorPalette | None = None,
        recommendations: RecommendationSet | None = None,
        profile_updates: dict[str, Any] | None = None,
    ) -> None:
        """Persist the turn: history, the latest snapshot, and profile deltas."""

        await self.append_message(session_id, user_message)
        await self.append_message(session_id, assistant_message)

        snapshot: dict[str, Any] = {}
        if skin_analysis is not None:
            snapshot["skin_analysis"] = skin_analysis.model_dump()
        if try_on is not None:
            snapshot["try_on"] = try_on.model_dump()
        if color_palette is not None:
            snapshot["color_palette"] = color_palette.model_dump()
        if recommendations is not None:
            snapshot["recommendations"] = recommendations.model_dump()

        if snapshot:
            try:
                await self._cache.write(
                    self._snapshot_key(session_id), json.dumps(snapshot), self._ttl
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("memory.snapshot_failed", session_id=session_id, error=str(exc))

        if profile_updates:
            try:
                await self._profiles.upsert(session_id, profile_updates)
            except Exception as exc:  # noqa: BLE001
                logger.warning("memory.profile_failed", session_id=session_id, error=str(exc))
