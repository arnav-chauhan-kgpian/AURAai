"""Health and readiness endpoints (unauthenticated, for orchestration)."""

from fastapi import APIRouter, Request, Response

from app.config.config import get_settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: the process is up. Never touches dependencies."""

    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request, response: Response) -> dict[str, object]:
    """Readiness: dependencies are reachable enough to serve traffic."""

    settings = get_settings()
    checks: dict[str, bool] = {}

    redis = getattr(request.app.state, "redis", None)
    if redis is not None:
        try:
            checks["redis"] = bool(await redis.ping())
        except Exception:  # noqa: BLE001
            checks["redis"] = False

    checks["agent"] = getattr(request.app.state, "aura_agent", None) is not None

    # Critical dependencies that must pass in production.
    critical = ["redis"] if settings.is_production else []
    ready_ok = all(checks.get(name, False) for name in critical)

    response.status_code = 200 if ready_ok else 503
    return {"status": "ready" if ready_ok else "not_ready", "checks": checks}
