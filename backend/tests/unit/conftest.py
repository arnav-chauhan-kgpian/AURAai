"""Fixtures for YouCam integration unit tests.

Provides a factory that builds a :class:`YouCamClient` wired to an in-memory
``httpx.MockTransport``, so tests exercise the real retry, polling and parsing
logic against scripted responses without any network access.
"""

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from app.config.config import Settings
from app.services.youcam_client import YouCamClient

Handler = Callable[[httpx.Request], httpx.Response]


def make_settings(**overrides: Any) -> Settings:
    """Build fast, deterministic settings for tests (no real backoff/waits)."""

    defaults: dict[str, Any] = dict(
        youcam_api_key="test-key",
        youcam_secret_key="test-secret",
        youcam_max_retries=3,
        youcam_retry_backoff_base_seconds=0.0,
        youcam_retry_backoff_max_seconds=0.0,
        youcam_poll_interval_seconds=0.0,
        youcam_poll_timeout_seconds=1.0,
        youcam_max_concurrent_requests=4,
    )
    defaults.update(overrides)
    return Settings(**defaults)


@pytest.fixture
def youcam() -> Callable[..., tuple[YouCamClient, Settings]]:
    """Return a factory: ``(handler, preseed=True, **overrides) -> (client, settings)``."""

    def factory(
        handler: Handler, *, preseed: bool = True, **overrides: Any
    ) -> tuple[YouCamClient, Settings]:
        settings = make_settings(**overrides)
        http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        client = YouCamClient(settings, http_client=http)
        if preseed:
            # Skip the RSA auth handshake; exercise request logic directly.
            client._token = "test-token"
            client._token_expiry = float("inf")
        return client, settings

    return factory
