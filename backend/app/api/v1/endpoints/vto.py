"""Virtual try-on endpoints."""

from fastapi import APIRouter, File, Form, UploadFile

from app.core.dependencies import VirtualTryOnServiceDep
from app.schemas.vto import TryOnResponse
from app.services.vto_service import DEFAULT_GARMENT_CATEGORY

router = APIRouter()


@router.post("/render", response_model=TryOnResponse)
async def render_try_on(
    service: VirtualTryOnServiceDep,
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    garment_category: str = Form(default=DEFAULT_GARMENT_CATEGORY),
    change_shoes: bool = Form(default=False),
) -> TryOnResponse:
    """Render the requested garment on the supplied person image.

    Runs the full YouCam workflow: upload both images, create the try-on task,
    poll to completion, and return the rendered output image URLs.
    """

    person = await person_image.read()
    garment = await garment_image.read()
    return await service.generate_tryon(
        user_image=person,
        clothing_image=garment,
        garment_category=garment_category,
        change_shoes=change_shoes,
        user_content_type=person_image.content_type or "image/jpeg",
        clothing_content_type=garment_image.content_type or "image/jpeg",
    )
