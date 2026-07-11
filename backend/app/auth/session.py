"""Session ownership and audit logging.

Phase 2 authorization: the conversation ``session_id`` is **server-owned**. A
client may present a previously-issued id, but it is only accepted after we
confirm it belongs to the authenticated user; otherwise a fresh id is minted.
This closes the "client-generated id" hole while staying usable in local dev
(no Supabase) where ownership can't be checked.
"""

from typing import Any

from app.auth.context import AuthContext
from app.config.config import Settings
from app.core.exceptions import ForbiddenError
from app.core.logging import get_logger
from app.db.repositories import AuditRepository, SessionRepository, new_id
from app.db.supabase import SupabaseClient

logger = get_logger(__name__)


class SessionService:
    """Resolves and validates ownership of conversation sessions."""

    def __init__(self, settings: Settings, supabase: SupabaseClient | None) -> None:
        self._settings = settings
        self._sessions = SessionRepository(supabase) if supabase is not None else None

    async def resolve(self, auth: AuthContext, requested_session_id: str | None) -> str:
        """Return a session id the caller is authorized to use."""

        if self._sessions is None:
            # Dev/degraded: cannot verify ownership without a database.
            if self._settings.is_production:
                raise ForbiddenError("Session store unavailable")
            return requested_session_id or new_id()

        if requested_session_id:
            row = await self._sessions.get(requested_session_id)
            if row is None:
                # Unknown id — treat as a request for a new session.
                return await self._sessions.create(
                    auth.user_id, auth.org_id, auth.clerk_session_id
                )
            if row.get("user_id") != auth.user_id or row.get("org_id") != auth.org_id:
                logger.warning(
                    "authz.session_ownership_denied",
                    user_id=auth.user_id,
                    session_id=requested_session_id,
                )
                raise ForbiddenError("You do not have access to this session")
            return requested_session_id

        return await self._sessions.create(auth.user_id, auth.org_id, auth.clerk_session_id)


class AuditLogger:
    """Best-effort append-only audit trail (never fails a request)."""

    def __init__(self, supabase: SupabaseClient | None) -> None:
        self._audit = AuditRepository(supabase) if supabase is not None else None

    async def record(
        self,
        *,
        user_id: str,
        org_id: str,
        session_id: str | None,
        action: str,
        resource: str | None = None,
        correlation_id: str | None = None,
        ip: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "user_id": user_id,
            "org_id": org_id,
            "session_id": session_id,
            "action": action,
            "resource": resource,
            "correlation_id": correlation_id,
            "ip_address": ip,
            "metadata": metadata or {},
        }
        if self._audit is None:
            logger.info("audit", **{k: v for k, v in entry.items() if v is not None})
            return
        try:
            await self._audit.log(entry)
        except Exception as exc:  # noqa: BLE001 - audit must never break a request
            logger.warning("audit.persist_failed", action=action, error=str(exc))
