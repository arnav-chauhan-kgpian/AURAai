"""Per-user daily quota.

A coarse daily cap on chat turns per authenticated user, layered on top of the
per-minute rate limiter. Its job is to protect scarce free-tier upstream quotas
(Groq TPM, YouCam credits) from a single user exhausting them. Keyed by user id
and the UTC day; anonymous callers are not counted (they can't be attributed).
Backed by the shared Redis client and **fails open** on any Redis error.

The current day is derived from the request-scoped timestamp Redis maintains, not
from wall-clock in the app, so it needs no local clock.
"""

from fastapi import Request

from app.auth.dependencies import get_auth_context
from app.config.config import get_settings
from app.core.exceptions import RateLimitedError
from app.core.logging import get_logger

logger = get_logger(__name__)

_DAY_SECONDS = 24 * 60 * 60


class DailyQuota:
    """Endpoint dependency enforcing a per-user daily request budget."""

    async def __call__(self, request: Request) -> None:
        settings = get_settings()
        limit = settings.daily_user_quota
        if limit <= 0:
            return
        redis = getattr(request.app.state, "redis", None)
        if redis is None:
            return

        try:
            auth = get_auth_context(request, settings)
        except Exception:  # noqa: BLE001 - quota only applies to known users
            return
        if auth.is_anonymous:
            return

        await enforce_daily_quota(redis, auth.user_id, limit)


async def enforce_daily_quota(redis, user_id: str, limit: int) -> None:
    """Increment and check a user's daily counter; raise when over budget.

    Fails open on any Redis error (availability over a best-effort control).
    """

    # Redis TIME gives a shared, monotonic day bucket without a local clock.
    try:
        day = await _redis_day(redis)
        key = f"aura:quota:{user_id}:{day}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, _DAY_SECONDS)
    except Exception as exc:  # noqa: BLE001 - fail open on quota outage
        logger.warning("quota.unavailable", error=str(exc))
        return

    if count > limit:
        logger.info("quota.exceeded", user_id=user_id, limit=limit)
        raise RateLimitedError(
            "Daily usage limit reached. Please try again tomorrow.",
            retry_after=_DAY_SECONDS,
        )


async def _redis_day(redis) -> int:
    """Return the current UTC day number from the Redis server clock."""

    seconds, _micros = await redis.time()
    return int(seconds) // _DAY_SECONDS
