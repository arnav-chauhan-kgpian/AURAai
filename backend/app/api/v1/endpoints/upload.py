"""Asset upload endpoints.

Exposes the YouCam File API directly so a client can pre-upload an image and
obtain a ``file_id`` for chaining into a task without re-uploading.
"""

from fastapi import APIRouter, File, Form, UploadFile

from app.core.dependencies import SettingsDep, UploadServiceDep
from app.schemas.upload import UploadResponse

router = APIRouter()


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    settings: SettingsDep,
    service: UploadServiceDep,
    file: UploadFile = File(...),
    kind: str = Form(default="skin"),
) -> UploadResponse:
    """Upload an image to the YouCam File API and return its ``file_id``.

    ``kind`` selects the File API endpoint: ``skin`` (default) or ``cloth``.
    """

    endpoint = (
        settings.youcam_file_cloth_url
        if kind == "cloth"
        else settings.youcam_file_skin_url
    )
    content = await file.read()
    return await service.upload(
        file_endpoint_url=endpoint,
        content=content,
        content_type=file.content_type or "application/octet-stream",
        file_name=file.filename or "upload",
    )
