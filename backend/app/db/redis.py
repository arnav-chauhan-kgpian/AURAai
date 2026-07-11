"""Redis client provider.

Provides an async Redis client used for agent memory, session state and caching
of upstream responses. Connections are created per request and closed by the
dependency layer.
"""

from redis.asyncio import Redis, from_url

from app.config.config import Settings

RedisClient = Redis


def get_redis_client(settings: Settings) -> RedisClient:
    """Build an async Redis client from application settings."""

    return from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
