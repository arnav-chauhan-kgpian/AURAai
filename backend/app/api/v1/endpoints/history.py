"""User history endpoints.

Returns the authenticated caller's persisted skin scans, try-on jobs and
recommendation snapshots — the data behind the History view and the skin
progress-over-time chart. Read-only and scoped to the caller by ``user_id``.
"""

from fastapi import APIRouter, Request

from app.auth.dependencies import RequestContextDep
from app.services.history_service import HistoryService

router = APIRouter()


def _service(request: Request) -> HistoryService:
    return HistoryService(
        getattr(request.app.state, "supabase", None),
        getattr(request.app.state, "object_store", None),
    )


@router.get("")
async def get_history(request: Request, ctx: RequestContextDep) -> dict[str, object]:
    """Return the caller's recent scans, try-ons and recommendations."""

    return await _service(request).fetch_history(ctx)
