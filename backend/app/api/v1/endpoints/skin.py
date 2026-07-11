"""Skin analysis endpoints (authenticated, rate-limited, upload-validated)."""

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from app.auth.dependencies import RequestContextDep
from app.core.dependencies import SkinServiceDep
from app.schemas.skin import SkinAnalysisResponse
from app.security.rate_limit import RateLimiter
from app.security.uploads import scan_for_viruses, validate_image_upload

router = APIRouter()
_rate_limit = RateLimiter()


@router.post("/analyze", response_model=SkinAnalysisResponse, dependencies=[Depends(_rate_limit)])
async def analyze_skin(
    request: Request,
    ctx: RequestContextDep,
    service: SkinServiceDep,
    file: UploadFile = File(...),
    concerns: list[str] | None = Form(default=None),
) -> SkinAnalysisResponse:
    """Analyse a user's facial skin and return scored concerns."""

    settings = request.app.state.settings
    content = await file.read()
    content_type = validate_image_upload(
        settings, content=content, content_type=file.content_type, filename=file.filename
    )
    await scan_for_viruses(settings, content)

    return await service.analyze(
        image=content,
        content_type=content_type,
        file_name=file.filename or "input.jpg",
        concerns=concerns,
    )
