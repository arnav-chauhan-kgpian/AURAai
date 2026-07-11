"""Authenticated request context models."""

from pydantic import BaseModel, ConfigDict, Field

from app.auth.roles import Role


class AuthContext(BaseModel):
    """The verified identity behind a request.

    Built from a Clerk JWT (or an anonymous dev fallback when auth is not
    required). ``session_id`` here is Clerk's session id (`sid`); the
    application's conversation session is resolved separately and validated for
    ownership — see :class:`RequestContext`.
    """

    model_config = ConfigDict(frozen=True)

    user_id: str
    org_id: str
    clerk_session_id: str | None = None
    role: Role = Role.USER
    email: str | None = None
    is_anonymous: bool = False


class RequestContext(BaseModel):
    """The fully resolved context every protected handler operates within."""

    model_config = ConfigDict(frozen=True)

    user_id: str
    org_id: str
    session_id: str = Field(description="Server-owned conversation session id")
    correlation_id: str
    role: Role = Role.USER
    is_anonymous: bool = False
