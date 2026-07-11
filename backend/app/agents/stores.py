"""Production memory backends.

Concrete implementations of the memory protocols in :mod:`app.agents.memory`:
Redis for the short-term session cache and Supabase for the durable profile
repository. Kept separate so ``memory.py`` (and its tests) never import the Redis
or Supabase SDKs.
"""

import asyncio
from typing import Any

from app.core.logging import get_logger
from app.db.redis import RedisClient
from app.db.supabase import SupabaseClient

logger = get_logger(__name__)


class RedisSessionCache:
    """Redis-backed :class:`~app.agents.memory.SessionCache`."""

    def __init__(self, redis: RedisClient) -> None:
        self._redis = redis

    async def read(self, key: str) -> str | None:
        return await self._redis.get(key)

    async def write(self, key: str, value: str, ttl: int) -> None:
        await self._redis.set(key, value, ex=ttl)

    async def append(self, key: str, value: str, ttl: int) -> None:
        await self._redis.rpush(key, value)
        await self._redis.expire(key, ttl)

    async def read_list(self, key: str, limit: int) -> list[str]:
        return await self._redis.lrange(key, -limit, -1)


class SupabaseProfileRepository:
    """Supabase-backed :class:`~app.agents.memory.ProfileRepository`."""

    def __init__(self, supabase: SupabaseClient, table: str = "stylist_profiles") -> None:
        self._supabase = supabase
        self._table = table

    async def fetch(self, session_id: str) -> dict[str, Any] | None:
        def _query() -> dict[str, Any] | None:
            response = (
                self._supabase.table(self._table)
                .select("*")
                .eq("session_id", session_id)
                .limit(1)
                .execute()
            )
            rows = response.data or []
            return rows[0] if rows else None

        return await asyncio.to_thread(_query)

    async def upsert(self, session_id: str, data: dict[str, Any]) -> None:
        payload = {**data, "session_id": session_id}

        def _write() -> None:
            self._supabase.table(self._table).upsert(payload, on_conflict="session_id").execute()

        await asyncio.to_thread(_write)
