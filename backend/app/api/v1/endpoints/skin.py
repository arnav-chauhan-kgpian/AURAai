"""Skin analysis endpoints."""

from fastapi import APIRouter, File, Form, UploadFile

from app.core.dependencies import SkinServiceDep
from app.schemas.skin import SkinAnalysisResponse

router = APIRouter()


@router.post("/analyze", response_model=SkinAnalysisResponse)
async def analyze_skin(
    service: SkinServiceDep,
    file: UploadFile = File(...),
    concerns: list[str] | None = Form(default=None),
) -> SkinAnalysisResponse:
    """Analyse a user's facial skin and return scored concerns.

    Runs the full YouCam workflow: upload the image, create the analysis task,
    poll to completion, and return the parsed scores and overlay images.
    """

    content = await file.read()
    return await service.analyze(
        image=content,
        content_type=file.content_type or "image/jpeg",
        file_name=file.filename or "input.jpg",
        concerns=concerns,
    )
