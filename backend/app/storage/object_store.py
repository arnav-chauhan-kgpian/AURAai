"""Object storage abstraction over Supabase Storage.

Persists user-uploaded images so they can be served via short-lived signed URLs,
deleted on request (GDPR), and swept by a retention job. All Supabase Storage
calls are sync, so they run in a worker thread.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from app.config.config import Settings
from app.core.logging import get_logger
from app.db.supabase import SupabaseClient

logger = get_logger(__name__)


class ObjectStore:
    """Bucket-scoped object storage backed by Supabase Storage."""

    def __init__(self, settings: Settings, supabase: SupabaseClient) -> None:
        self._settings = settings
        self._supabase = supabase
        self._bucket = settings.supabase_storage_bucket

    def _client(self):
        return self._supabase.storage.from_(self._bucket)

    async def put(self, key: str, content: bytes, content_type: str) -> str:
        """Store bytes at ``key`` and return the key."""

        def _upload() -> None:
            self._client().upload(
                key,
                content,
                {"content-type": content_type, "upsert": "true"},
            )

        await asyncio.to_thread(_upload)
        logger.info("storage.put", key=key, size_bytes=len(content))
        return key

    async def signed_url(self, key: str, expires_in: int | None = None) -> str:
        """Return a time-limited signed URL for the given object key."""

        ttl = expires_in or self._settings.signed_url_ttl_seconds

        def _sign() -> str:
            resp = self._client().create_signed_url(key, ttl)
            return resp.get("signedURL") or resp.get("signedUrl") or ""

        return await asyncio.to_thread(_sign)

    async def delete(self, keys: list[str]) -> None:
        """Permanently remove objects."""

        if not keys:
            return

        def _remove() -> None:
            self._client().remove(keys)

        await asyncio.to_thread(_remove)
        logger.info("storage.delete", count=len(keys))

    async def list_prefix(self, prefix: str) -> list[dict[str, Any]]:
        def _list() -> list[dict[str, Any]]:
            return self._client().list(prefix) or []

        return await asyncio.to_thread(_list)

    async def purge_expired(self, prefix: str = "") -> int:
        """Delete objects older than the configured retention window."""

        cutoff = datetime.now(UTC) - timedelta(days=self._settings.image_retention_days)
        objects = await self.list_prefix(prefix)
        stale: list[str] = []
        for obj in objects:
            created = _parse_time(obj.get("created_at"))
            if created and created < cutoff:
                name = obj.get("name")
                if name:
                    stale.append(f"{prefix}/{name}" if prefix else name)
        await self.delete(stale)
        logger.info("storage.purge", prefix=prefix or "root", deleted=len(stale))
        return len(stale)


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
