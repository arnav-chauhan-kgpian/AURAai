"""Role-based access control groundwork.

A small, explicit role model so endpoints can gate access today and the scheme
can grow without rework. Roles are sourced from Clerk organization claims
(`org_role`) and any custom `roles` claim.
"""

from enum import Enum


class Role(str, Enum):
    """Coarse-grained roles, ordered from least to most privileged."""

    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"


# Privilege ordering for "at least this role" checks.
_ORDER = {Role.USER: 0, Role.ADMIN: 1, Role.OWNER: 2}

# Map Clerk organization role slugs onto app roles.
_CLERK_ROLE_MAP = {
    "org:admin": Role.ADMIN,
    "org:owner": Role.OWNER,
    "admin": Role.ADMIN,
    "owner": Role.OWNER,
    "org:member": Role.USER,
    "member": Role.USER,
}


def normalize_role(value: str | None) -> Role:
    """Map a raw Clerk role slug to an app :class:`Role` (defaults to USER)."""

    if not value:
        return Role.USER
    return _CLERK_ROLE_MAP.get(value.lower(), Role.USER)


def role_satisfies(actual: Role, required: Role) -> bool:
    """Return whether ``actual`` meets or exceeds ``required``."""

    return _ORDER[actual] >= _ORDER[required]
