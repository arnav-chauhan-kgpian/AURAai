"""Redis-backed rate limiting.

A fixed-window limiter keyed by authenticated user (falling back to client IP).
It reuses the application's shared Redis client and **fails open** on a Redis
outage — availability of the product is not sacrificed for a best-effort control,
though the failure is logged.
"""

from fastapi import Request

from app.auth.dependencies import client_ip, get_auth_context
from app.config.config import get_settings
from app.core.exceptions import RateLimitedError
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """A per-endpoint dependency enforcing N requests per rolling minute."""

    def __init__(self, limit: int | None = None, window_seconds: int = 60) -> None:
        self._limit = limit
        self._window = window_seconds

    async def __call__(self, request: Request) -> None:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return
        limit = self._limit or settings.rate_limit_per_minute
        redis = getattr(request.app.state, "redis", None)
        if redis is None:
            return

        identity = _identity(request)
        bucket = request.scope.get("path", "*")
        key = f"aura:rl:{bucket}:{identity}"

        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, self._window)
        except Exception as exc:  # noqa: BLE001 - fail open on limiter outage
            logger.warning("ratelimit.unavailable", error=str(exc))
            return

        if count > limit:
            ttl = await _safe_ttl(redis, key, self._window)
            logger.info("ratelimit.exceeded", identity=identity, path=bucket)
            raise RateLimitedError("Rate limit exceeded", retry_after=ttl)


def _identity(request: Request) -> str:
    try:
        auth = get_auth_context(request, get_settings())
        if not auth.is_anonymous:
            return f"user:{auth.user_id}"
    except Exception:  # noqa: BLE001 - identity for limiting only
        pass
    return f"ip:{client_ip(request) or 'unknown'}"


async def _safe_ttl(redis, key: str, default: int) -> int:
    try:
        ttl = await redis.ttl(key)
        return ttl if isinstance(ttl, int) and ttl > 0 else default
    except Exception:  # noqa: BLE001
        return default
