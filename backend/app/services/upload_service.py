"""Upload service.

Implements the YouCam File API handshake: request a presigned upload target,
PUT the binary image to it, and return the resulting ``file_id`` that AI tasks
reference. Capability services (skin, try-on) delegate all uploads here so the
two-step upload protocol lives in exactly one place.
"""

from app.config.config import Settings
from app.core.logging import get_logger
from app.schemas.upload import UploadResponse
from app.services.youcam_client import YouCamClient

logger = get_logger(__name__)


class UploadService:
    """Uploads image assets to the YouCam File API."""

    def __init__(self, settings: Settings, client: YouCamClient) -> None:
        self._settings = settings
        self._client = client

    async def upload(
        self,
        file_endpoint_url: str,
        content: bytes,
        content_type: str,
        file_name: str,
    ) -> UploadResponse:
        """Upload an image and return its ``file_id``.

        Args:
            file_endpoint_url: The File API URL for the target capability
                (e.g. ``settings.youcam_file_skin_url``).
            content: Raw image bytes.
            content_type: MIME type of the image (e.g. ``image/jpeg``).
            file_name: A name for the asset, echoed back for traceability.
        """

        target = await self._client.request_upload_target(
            file_endpoint_url, file_name, content_type
        )
        await self._client.upload_binary(target, content, content_type)

        logger.info(
            "upload.completed",
            file_id=target.file_id,
            file_name=file_name,
            content_type=content_type,
            size_bytes=len(content),
        )
        return UploadResponse(
            file_id=target.file_id,
            file_name=file_name,
            content_type=content_type,
            size_bytes=len(content),
        )
