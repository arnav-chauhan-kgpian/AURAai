"""In-process data-retention sweeper.

Free-tier deployments have no external scheduler, so retention runs as a
long-lived asyncio task inside the app: on an interval it asks object storage to
purge objects older than the configured window (:attr:`Settings.image_retention_days`).
It is best-effort — a failed sweep is logged and retried next cycle — and is a
no-op when disabled or when storage is unavailable (local dev).
"""

import asyncio
import contextlib

from app.config.config import Settings
from app.core.logging import get_logger
from app.storage.object_store import ObjectStore

logger = get_logger(__name__)


class RetentionScheduler:
    """Periodically purges expired stored objects."""

    def __init__(self, settings: Settings, object_store: ObjectStore | None) -> None:
        self._settings = settings
        self._store = object_store
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if not self._settings.retention_sweep_enabled or self._store is None:
            return
        self._task = asyncio.create_task(self._loop())
        logger.info(
            "retention.scheduler_started",
            interval_hours=self._settings.retention_sweep_interval_hours,
            retention_days=self._settings.image_retention_days,
        )

    async def _loop(self) -> None:
        interval = max(self._settings.retention_sweep_interval_hours, 1) * 3600
        while True:
            try:
                assert self._store is not None
                deleted = await self._store.purge_expired()
                logger.info("retention.sweep_done", deleted=deleted)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - retry on the next cycle
                logger.warning("retention.sweep_failed", error=str(exc))
            await asyncio.sleep(interval)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self._task
        self._task = None
