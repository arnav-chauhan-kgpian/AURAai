"""Privacy operations: consent, image deletion, and GDPR erasure.

Implements the user's data rights over face imagery (biometric data): recording
consent, deleting stored images on demand, and a full account erasure that
soft-deletes records across every table and purges stored objects. Degrades
safely when Supabase is not configured (dev), where there is nothing to erase.
"""

import asyncio
from typing import Any

from app.config.config import Settings
from app.core.logging import get_logger
from app.db.supabase import SupabaseClient
from app.storage.object_store import ObjectStore

logger = get_logger(__name__)

# Tables that hold user-scoped data, erased on account deletion.
_USER_TABLES = (
    "profiles",
    "sessions",
    "conversations",
    "skin_scans",
    "try_on_jobs",
    "recommendations",
)


class PrivacyService:
    """Consent and data-erasure operations."""

    def __init__(
        self, settings: Settings, supabase: SupabaseClient | None, store: ObjectStore | None
    ) -> None:
        self._settings = settings
        self._db = supabase
        self._store = store

    async def get_consent(self, user_id: str) -> dict[str, Any]:
        if self._db is None:
            return {"granted": False, "source": "unavailable"}

        def _q() -> dict[str, Any]:
            resp = (
                self._db.table("profiles")
                .select("consent_granted, consent_at")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            rows = resp.data or []
            return rows[0] if rows else {"consent_granted": False, "consent_at": None}

        row = await asyncio.to_thread(_q)
        return {"granted": bool(row.get("consent_granted")), "at": row.get("consent_at")}

    async def set_consent(self, user_id: str, org_id: str, granted: bool) -> dict[str, Any]:
        if self._db is None:
            return {"granted": granted, "persisted": False}

        def _w() -> None:
            self._db.table("profiles").upsert(
                {
                    "user_id": user_id,
                    "org_id": org_id,
                    "consent_granted": granted,
                    "consent_at": "now()",
                },
                on_conflict="user_id",
            ).execute()

        await asyncio.to_thread(_w)
        logger.info("privacy.consent_set", user_id=user_id, granted=granted)
        return {"granted": granted, "persisted": True}

    async def delete_user_images(self, user_id: str) -> dict[str, Any]:
        deleted = 0
        if self._store is not None:
            objects = await self._store.list_prefix(user_id)
            keys = [f"{user_id}/{o['name']}" for o in objects if o.get("name")]
            await self._store.delete(keys)
            deleted = len(keys)
        if self._db is not None:
            await self._soft_delete("skin_scans", user_id)
            await self._soft_delete("try_on_jobs", user_id)
        logger.info("privacy.images_deleted", user_id=user_id, count=deleted)
        return {"images_deleted": deleted}

    async def delete_account(self, user_id: str) -> dict[str, Any]:
        """GDPR erasure: soft-delete all records and purge stored images."""

        purged = await self.delete_user_images(user_id)
        erased: list[str] = []
        if self._db is not None:
            for table in _USER_TABLES:
                await self._soft_delete(table, user_id)
                erased.append(table)
        logger.info("privacy.account_deleted", user_id=user_id, tables=erased)
        return {"erased_tables": erased, **purged}

    async def _soft_delete(self, table: str, user_id: str) -> None:
        if self._db is None:
            return

        def _w() -> None:
            self._db.table(table).update({"deleted_at": "now()"}).eq("user_id", user_id).execute()

        try:
            await asyncio.to_thread(_w)
        except Exception as exc:  # noqa: BLE001 - continue erasing other tables
            logger.warning("privacy.soft_delete_failed", table=table, error=str(exc))
