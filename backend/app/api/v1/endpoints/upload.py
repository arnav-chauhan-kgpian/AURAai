"""Asset upload endpoints (authenticated, rate-limited, upload-validated).

Exposes the YouCam File API directly so a client can pre-upload an image and
obtain a ``file_id`` for chaining into a task without re-uploading.
"""

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from app.auth.dependencies import RequestContextDep, SettingsDep
from app.core.dependencies import UploadServiceDep
from app.schemas.upload import UploadResponse
from app.security.rate_limit import RateLimiter
from app.security.uploads import scan_for_viruses, validate_image_upload

router = APIRouter()
_rate_limit = RateLimiter()


@router.post("/image", response_model=UploadResponse, dependencies=[Depends(_rate_limit)])
async def upload_image(
    request: Request,
    ctx: RequestContextDep,
    settings: SettingsDep,
    service: UploadServiceDep,
    file: UploadFile = File(...),
    kind: str = Form(default="skin"),
) -> UploadResponse:
    """Upload an image to the YouCam File API and return its ``file_id``.

    ``kind`` selects the File API endpoint: ``skin`` (default) or ``cloth``.
    """

    content = await file.read()
    content_type = validate_image_upload(
        settings, content=content, content_type=file.content_type, filename=file.filename
    )
    await scan_for_viruses(settings, content)

    endpoint = (
        settings.youcam_file_cloth_url if kind == "cloth" else settings.youcam_file_skin_url
    )
    return await service.upload(
        file_endpoint_url=endpoint,
        content=content,
        content_type=content_type,
        file_name=file.filename or "upload",
    )
