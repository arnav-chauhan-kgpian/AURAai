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


class UserRepository:
    """Upsert of the `users` parent row (required by FK-constrained tables)."""

    def __init__(self, supabase: SupabaseClient) -> None:
        self._db = supabase

    async def ensure(self, user_id: str, org_id: str, email: str | None = None) -> None:
        def _w() -> None:
            self._db.table("users").upsert(
                {"id": user_id, "org_id": org_id, "email": email}, on_conflict="id"
            ).execute()

        await asyncio.to_thread(_w)


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


class ConversationRepository:
    """Append conversation turns for history and continuity."""

    def __init__(self, supabase: SupabaseClient) -> None:
        self._db = supabase

    async def add(
        self, *, session_id: str, user_id: str, org_id: str, role: str, content: str
    ) -> None:
        def _w() -> None:
            self._db.table("conversations").insert(
                {
                    "id": new_id(),
                    "session_id": session_id,
                    "user_id": user_id,
                    "org_id": org_id,
                    "role": role,
                    "content": content,
                }
            ).execute()

        await asyncio.to_thread(_w)

    async def list_for_session(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        def _q() -> list[dict[str, Any]]:
            resp = (
                self._db.table("conversations")
                .select("role, content, created_at")
                .eq("session_id", session_id)
                .is_("deleted_at", "null")
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )
            return resp.data or []

        return await asyncio.to_thread(_q)


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

    async def list_for_user(self, user_id: str, limit: int = 30) -> list[dict[str, Any]]:
        def _q() -> list[dict[str, Any]]:
            resp = (
                self._db.table("skin_scans")
                .select("id, task_id, scores, overlays, created_at")
                .eq("user_id", user_id)
                .is_("deleted_at", "null")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return resp.data or []

        return await asyncio.to_thread(_q)

    async def soft_delete_for_user(self, user_id: str) -> None:
        def _w() -> None:
            self._db.table("skin_scans").update({"deleted_at": "now()"}).eq(
                "user_id", user_id
            ).execute()

        await asyncio.to_thread(_w)


class TryOnRepository:
    """`try_on_jobs` records for virtual try-on history."""

    def __init__(self, supabase: SupabaseClient) -> None:
        self._db = supabase

    async def create(self, record: dict[str, Any]) -> str:
        job_id = new_id()

        def _w() -> None:
            self._db.table("try_on_jobs").insert({"id": job_id, **record}).execute()

        await asyncio.to_thread(_w)
        return job_id

    async def list_for_user(self, user_id: str, limit: int = 30) -> list[dict[str, Any]]:
        def _q() -> list[dict[str, Any]]:
            resp = (
                self._db.table("try_on_jobs")
                .select("id, task_id, status, output_images, created_at")
                .eq("user_id", user_id)
                .is_("deleted_at", "null")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return resp.data or []

        return await asyncio.to_thread(_q)


class RecommendationRepository:
    """`recommendations` snapshots per turn."""

    def __init__(self, supabase: SupabaseClient) -> None:
        self._db = supabase

    async def create(self, record: dict[str, Any]) -> str:
        rec_id = new_id()

        def _w() -> None:
            self._db.table("recommendations").insert({"id": rec_id, **record}).execute()

        await asyncio.to_thread(_w)
        return rec_id

    async def list_for_user(self, user_id: str, limit: int = 20) -> list[dict[str, Any]]:
        def _q() -> list[dict[str, Any]]:
            resp = (
                self._db.table("recommendations")
                .select("id, payload, created_at")
                .eq("user_id", user_id)
                .is_("deleted_at", "null")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return resp.data or []

        return await asyncio.to_thread(_q)
