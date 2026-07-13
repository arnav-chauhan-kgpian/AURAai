"""Per-user daily quota logic."""

import pytest

from app.core.exceptions import RateLimitedError
from app.security.quota import enforce_daily_quota


class FakeRedis:
    def __init__(self, fail: bool = False) -> None:
        self.counts: dict[str, int] = {}
        self.expires: dict[str, int] = {}
        self._fail = fail

    async def time(self) -> tuple[int, int]:
        if self._fail:
            raise RuntimeError("redis down")
        return (1_700_000_000, 0)  # fixed day bucket

    async def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, ttl: int) -> None:
        self.expires[key] = ttl


@pytest.mark.asyncio
async def test_under_limit_passes() -> None:
    redis = FakeRedis()
    for _ in range(3):
        await enforce_daily_quota(redis, "user_1", limit=5)
    # First call set an expiry on the day key.
    assert any(v == 24 * 60 * 60 for v in redis.expires.values())


@pytest.mark.asyncio
async def test_over_limit_raises() -> None:
    redis = FakeRedis()
    for _ in range(2):
        await enforce_daily_quota(redis, "user_1", limit=2)
    with pytest.raises(RateLimitedError):
        await enforce_daily_quota(redis, "user_1", limit=2)


@pytest.mark.asyncio
async def test_separate_users_have_separate_budgets() -> None:
    redis = FakeRedis()
    await enforce_daily_quota(redis, "user_1", limit=1)
    # A different user is unaffected by user_1 hitting the cap.
    await enforce_daily_quota(redis, "user_2", limit=1)


@pytest.mark.asyncio
async def test_fails_open_on_redis_error() -> None:
    redis = FakeRedis(fail=True)
    # Must not raise even though Redis is unavailable.
    await enforce_daily_quota(redis, "user_1", limit=1)
