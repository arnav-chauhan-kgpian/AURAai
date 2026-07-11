"""Privacy & data-rights endpoints (consent, deletion, GDPR erasure)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.auth.dependencies import RequestContextDep
from app.core.logging import get_logger
from app.schemas.common import APIModel
from app.services.privacy_service import PrivacyService

router = APIRouter()
logger = get_logger(__name__)


class ConsentRequest(BaseModel):
    granted: bool


class ConsentStatus(APIModel):
    granted: bool


def _service(request: Request) -> PrivacyService:
    return PrivacyService(
        request.app.state.settings,
        getattr(request.app.state, "supabase", None),
        getattr(request.app.state, "object_store", None),
    )


@router.get("/consent")
async def get_consent(request: Request, ctx: RequestContextDep) -> dict[str, object]:
    """Return the caller's current biometric-data consent status."""

    return await _service(request).get_consent(ctx.user_id)


@router.post("/consent", response_model=ConsentStatus)
async def set_consent(
    request: Request, ctx: RequestContextDep, body: ConsentRequest
) -> ConsentStatus:
    """Record (grant or withdraw) consent to process face imagery."""

    result = await _service(request).set_consent(ctx.user_id, ctx.org_id, body.granted)
    await request.app.state.audit.record(
        user_id=ctx.user_id,
        org_id=ctx.org_id,
        session_id=ctx.session_id,
        action="consent.set",
        correlation_id=ctx.correlation_id,
        metadata={"granted": body.granted},
    )
    return ConsentStatus(granted=bool(result["granted"]))


@router.delete("/images")
async def delete_images(request: Request, ctx: RequestContextDep) -> dict[str, object]:
    """Delete all stored images for the caller."""

    result = await _service(request).delete_user_images(ctx.user_id)
    await request.app.state.audit.record(
        user_id=ctx.user_id,
        org_id=ctx.org_id,
        session_id=ctx.session_id,
        action="images.delete",
        correlation_id=ctx.correlation_id,
        metadata=result,
    )
    return result


@router.delete("/account")
async def delete_account(request: Request, ctx: RequestContextDep) -> dict[str, object]:
    """GDPR erasure: delete the caller's data across all tables and storage."""

    result = await _service(request).delete_account(ctx.user_id)
    await request.app.state.audit.record(
        user_id=ctx.user_id,
        org_id=ctx.org_id,
        session_id=ctx.session_id,
        action="account.delete",
        correlation_id=ctx.correlation_id,
        metadata=result,
    )
    logger.info("privacy.gdpr_erasure", user_id=ctx.user_id)
    return {"status": "erased", **result}
