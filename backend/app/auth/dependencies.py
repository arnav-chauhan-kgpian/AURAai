"""FastAPI auth dependencies: identity, request context, and RBAC.

These providers turn an incoming request into a verified :class:`AuthContext` and
a fully-resolved :class:`RequestContext` (user_id + org_id + server-owned
session_id + correlation_id). Handlers depend on ``RequestContextDep`` and never
touch raw tokens or client-supplied ids.
"""

from typing import Annotated

from fastapi import Depends, Request

from app.auth.context import AuthContext, RequestContext
from app.auth.roles import Role, role_satisfies
from app.auth.session import SessionService
from app.config.config import Settings, get_settings
from app.core.exceptions import ForbiddenError, UnauthenticatedError
from app.core.logging import get_logger

logger = get_logger(__name__)

SettingsDep = Annotated[Settings, Depends(get_settings)]

_SESSION_HEADER = "X-Session-Id"
_ANONYMOUS = AuthContext(
    user_id="anonymous", org_id="anonymous", role=Role.USER, is_anonymous=True
)


def _bearer_token(request: Request) -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip()
    # Clerk also sets a `__session` cookie for same-site requests.
    return request.cookies.get("__session")


def get_auth_context(request: Request, settings: SettingsDep) -> AuthContext:
    """Verify the caller's identity, or fall back to anonymous in dev."""

    token = _bearer_token(request)
    verifier = getattr(request.app.state, "clerk_verifier", None)

    if token and verifier is not None and verifier.configured:
        return verifier.verify(token)

    if settings.auth_required:
        raise UnauthenticatedError("Authentication required")

    return _ANONYMOUS


AuthDep = Annotated[AuthContext, Depends(get_auth_context)]


async def get_request_context(
    request: Request, auth: AuthDep, settings: SettingsDep
) -> RequestContext:
    """Resolve and authorize the full per-request context."""

    session_service: SessionService = request.app.state.session_service
    requested = request.headers.get(_SESSION_HEADER)
    session_id = await session_service.resolve(auth, requested)
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    return RequestContext(
        user_id=auth.user_id,
        org_id=auth.org_id,
        session_id=session_id,
        correlation_id=correlation_id,
        role=auth.role,
        is_anonymous=auth.is_anonymous,
    )


RequestContextDep = Annotated[RequestContext, Depends(get_request_context)]


def require_role(minimum: Role):
    """Dependency factory enforcing a minimum role."""

    def _guard(ctx: RequestContextDep) -> RequestContext:
        if not role_satisfies(ctx.role, minimum):
            raise ForbiddenError(f"Requires {minimum.value} role")
        return ctx

    return _guard


def client_ip(request: Request) -> str | None:
    """Best-effort client IP, honoring a single upstream proxy hop."""

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
