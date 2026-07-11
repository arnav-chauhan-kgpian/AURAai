"""Supabase-backed repositories for the production data model.

Thin, typed data-access helpers over the tables defined in the migrations
(`sessions`, `audit_logs`, `skin_scans`, `try_on_jobs`, …). Every call is
wrapped with :func:`asyncio.to_thread` because the Supabase client is sync.
Callers use :class:`SessionService`, which degrades gracefully when Supabase is
not configured (local dev) so the app remains runnable without a database.
"""

import asyncio
import uuid
from typing import Any

from app.core.logging import get_logger
from app.db.supabase import SupabaseClient

logger = get_logger(__name__)


def new_id() -> str:
    """Generate a server-side identifier (never trust a client for these)."""

    return uuid.uuid4().hex


class SessionRepository:
    """CRUD for conversation `sessions`."""

    def __init__(self, supabase: SupabaseClient) -> None:
        self._db = supabase

    async def get(self, session_id: str) -> dict[str, Any] | None:
        def _q() -> dict[str, Any] | None:
            resp = (
                self._db.table("sessions")
                .select("*")
                .eq("id", session_id)
                .is_("deleted_at", "null")
                .limit(1)
                .execute()
            )
            rows = resp.data or []
            return rows[0] if rows else None

        return await asyncio.to_thread(_q)

    async def create(self, user_id: str, org_id: str, clerk_session_id: str | None) -> str:
        session_id = new_id()

        def _w() -> None:
            self._db.table("sessions").insert(
                {
                    "id": session_id,
                    "user_id": user_id,
                    "org_id": org_id,
                    "clerk_session_id": clerk_session_id,
                }
            ).execute()

        await asyncio.to_thread(_w)
        return session_id


class AuditRepository:
    """Append-only `audit_logs`."""

    def __init__(self, supabase: SupabaseClient) -> None:
        self._db = supabase

    async def log(self, entry: dict[str, Any]) -> None:
        def _w() -> None:
            self._db.table("audit_logs").insert({"id": new_id(), **entry}).execute()

        await asyncio.to_thread(_w)


class ScanRepository:
    """`skin_scans` records (metadata only — never raw biometric pixels)."""

    def __init__(self, supabase: SupabaseClient) -> None:
        self._db = supabase

    async def create(self, record: dict[str, Any]) -> str:
        scan_id = new_id()

        def _w() -> None:
            self._db.table("skin_scans").insert({"id": scan_id, **record}).execute()

        await asyncio.to_thread(_w)
        return scan_id

    async def soft_delete_for_user(self, user_id: str) -> None:
        def _w() -> None:
            self._db.table("skin_scans").update({"deleted_at": "now()"}).eq(
                "user_id", user_id
            ).execute()

        await asyncio.to_thread(_w)
