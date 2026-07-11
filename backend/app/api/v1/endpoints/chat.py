"""Conversational stylist agent endpoints (authenticated, rate-limited).

Handlers contain no business logic beyond marshalling a validated, authorized
request into the agent. Identity, the server-owned session id, upload validation,
consent, and rate limiting are all enforced here before the agent runs.
"""

import json

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.auth.context import RequestContext
from app.auth.dependencies import RequestContextDep, client_ip
from app.core.dependencies import AuraAgentDep
from app.core.exceptions import ForbiddenError
from app.schemas.agent import AgentImages
from app.schemas.chat import ChatResponse
from app.security.rate_limit import RateLimiter
from app.security.sanitize import sanitize_text
from app.security.uploads import scan_for_viruses, validate_image_upload
from app.services.privacy_service import PrivacyService

router = APIRouter()
_rate_limit = RateLimiter()


async def _validated_image(
    request: Request, file: UploadFile | None
) -> tuple[bytes | None, str]:
    """Read, validate and virus-scan an uploaded image."""

    if file is None:
        return None, "image/jpeg"
    settings = request.app.state.settings
    content = await file.read()
    content_type = validate_image_upload(
        settings, content=content, content_type=file.content_type, filename=file.filename
    )
    await scan_for_viruses(settings, content)
    return content, content_type


async def _ensure_consent(request: Request, ctx: RequestContext) -> None:
    settings = request.app.state.settings
    supabase = getattr(request.app.state, "supabase", None)
    if not settings.consent_required or supabase is None or ctx.is_anonymous:
        return
    consent = await PrivacyService(settings, supabase, None).get_consent(ctx.user_id)
    if not consent.get("granted"):
        raise ForbiddenError("Consent to process face images is required")


async def _build_images(
    request: Request,
    ctx: RequestContext,
    face_image: UploadFile | None,
    garment_image: UploadFile | None,
    garment_category: str,
) -> AgentImages:
    face, face_type = await _validated_image(request, face_image)
    garment, garment_type = await _validated_image(request, garment_image)
    if face is not None:
        await _ensure_consent(request, ctx)
    return AgentImages(
        face_image=face,
        face_content_type=face_type,
        garment_image=garment,
        garment_content_type=garment_type,
        garment_category=garment_category,
    )


@router.post("", response_model=ChatResponse, dependencies=[Depends(_rate_limit)])
async def chat(
    request: Request,
    ctx: RequestContextDep,
    agent: AuraAgentDep,
    message: str = Form(...),
    face_image: UploadFile | None = File(default=None),
    garment_image: UploadFile | None = File(default=None),
    garment_category: str = Form(default="upper_body"),
) -> ChatResponse:
    """Run one turn of the autonomous stylist agent."""

    clean_message = sanitize_text(message, field="message")
    images = await _build_images(request, ctx, face_image, garment_image, garment_category)

    response = await agent.run(session_id=ctx.session_id, message=clean_message, images=images)

    await request.app.state.audit.record(
        user_id=ctx.user_id,
        org_id=ctx.org_id,
        session_id=ctx.session_id,
        action="chat.run",
        correlation_id=ctx.correlation_id,
        ip=client_ip(request),
        metadata={"intent": response.intent, "tools": response.tools_used},
    )
    return response


@router.post("/stream", dependencies=[Depends(_rate_limit)])
async def chat_stream(
    request: Request,
    ctx: RequestContextDep,
    agent: AuraAgentDep,
    message: str = Form(...),
    face_image: UploadFile | None = File(default=None),
    garment_image: UploadFile | None = File(default=None),
    garment_category: str = Form(default="upper_body"),
) -> StreamingResponse:
    """Run one turn, streaming intent, tool steps and reply tokens as SSE."""

    clean_message = sanitize_text(message, field="message")
    images = await _build_images(request, ctx, face_image, garment_image, garment_category)

    async def event_stream():
        async for event in agent.stream(
            session_id=ctx.session_id, message=clean_message, images=images
        ):
            yield f"data: {json.dumps(event.model_dump())}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"X-Session-Id": ctx.session_id, "Cache-Control": "no-cache"},
    )
