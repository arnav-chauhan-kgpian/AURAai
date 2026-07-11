"""Clerk JWT verification.

Verifies short-lived Clerk session tokens (RS256) against Clerk's JWKS, checking
signature, issuer, expiry and authorized party. Clerk owns refresh tokens and
secure-cookie rotation on the client; the backend only trusts the verified JWT.
Signing keys are cached by ``PyJWKClient``.
"""

from typing import Any

import jwt
from jwt import PyJWKClient

from app.auth.context import AuthContext
from app.auth.roles import normalize_role
from app.config.config import Settings
from app.core.exceptions import UnauthenticatedError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClerkVerifier:
    """Verifies Clerk-issued JWTs and maps claims to an :class:`AuthContext`."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._issuer = settings.clerk_issuer.rstrip("/") if settings.clerk_issuer else ""
        self._authorized_parties = set(settings.clerk_authorized_parties)
        jwks_url = settings.resolved_clerk_jwks_url
        self._jwks: PyJWKClient | None = (
            PyJWKClient(jwks_url, cache_keys=True, lifespan=settings.jwks_cache_seconds)
            if jwks_url
            else None
        )

    @property
    def configured(self) -> bool:
        return self._jwks is not None

    def verify(self, token: str) -> AuthContext:
        """Verify a bearer token and return the caller's identity."""

        if not self._jwks:
            raise UnauthenticatedError("Authentication is not configured")

        try:
            signing_key = self._jwks.get_signing_key_from_jwt(token)
            claims: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self._issuer or None,
                options={"verify_aud": False, "require": ["exp", "iat", "sub"]},
                leeway=10,
            )
        except jwt.PyJWTError as exc:
            logger.info("auth.token_rejected", error=str(exc))
            raise UnauthenticatedError("Invalid or expired token") from exc

        self._check_authorized_party(claims)
        return self._to_context(claims)

    def _check_authorized_party(self, claims: dict[str, Any]) -> None:
        azp = claims.get("azp")
        if self._authorized_parties and azp and azp not in self._authorized_parties:
            logger.warning("auth.untrusted_party", azp=azp)
            raise UnauthenticatedError("Untrusted authorized party")

    @staticmethod
    def _to_context(claims: dict[str, Any]) -> AuthContext:
        user_id = str(claims["sub"])
        org_id = str(claims.get("org_id") or f"personal:{user_id}")
        return AuthContext(
            user_id=user_id,
            org_id=org_id,
            clerk_session_id=claims.get("sid"),
            role=normalize_role(claims.get("org_role") or _first_role(claims.get("roles"))),
            email=claims.get("email"),
            is_anonymous=False,
        )


def _first_role(roles: Any) -> str | None:
    if isinstance(roles, list) and roles:
        return str(roles[0])
    if isinstance(roles, str):
        return roles
    return None
