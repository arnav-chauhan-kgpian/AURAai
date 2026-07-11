"""Virtual try-on endpoints (authenticated, rate-limited, upload-validated)."""

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from app.auth.dependencies import RequestContextDep
from app.core.dependencies import VirtualTryOnServiceDep
from app.schemas.vto import TryOnResponse
from app.security.rate_limit import RateLimiter
from app.security.uploads import scan_for_viruses, validate_image_upload
from app.services.vto_service import DEFAULT_GARMENT_CATEGORY

router = APIRouter()
_rate_limit = RateLimiter()


@router.post("/render", response_model=TryOnResponse, dependencies=[Depends(_rate_limit)])
async def render_try_on(
    request: Request,
    ctx: RequestContextDep,
    service: VirtualTryOnServiceDep,
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    garment_category: str = Form(default=DEFAULT_GARMENT_CATEGORY),
    change_shoes: bool = Form(default=False),
) -> TryOnResponse:
    """Render the requested garment on the supplied person image."""

    settings = request.app.state.settings
    person = await person_image.read()
    garment = await garment_image.read()
    person_type = validate_image_upload(
        settings,
        content=person,
        content_type=person_image.content_type,
        filename=person_image.filename,
    )
    garment_type = validate_image_upload(
        settings,
        content=garment,
        content_type=garment_image.content_type,
        filename=garment_image.filename,
    )
    await scan_for_viruses(settings, person)
    await scan_for_viruses(settings, garment)

    return await service.generate_tryon(
        user_image=person,
        clothing_image=garment,
        garment_category=garment_category,
        change_shoes=change_shoes,
        user_content_type=person_type,
        clothing_content_type=garment_type,
    )
