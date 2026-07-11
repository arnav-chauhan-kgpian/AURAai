"""Apparel virtual try-on service.

Orchestrates the complete YouCam Apparel Virtual Try-On workflow — upload the
person and garment images, create the try-on task, poll until it completes, and
parse the rendered output image URLs into domain schemas.
"""

from typing import Any

from app.config.config import Settings
from app.core.logging import get_logger
from app.schemas.vto import TryOnResponse
from app.services.upload_service import UploadService
from app.services.youcam_client import YouCamClient
from app.utils.parsing import IMAGE_EXTENSIONS, collect_urls

logger = get_logger(__name__)

# Default apparel category; YouCam distinguishes upper/lower/full body garments.
DEFAULT_GARMENT_CATEGORY = "upper_body"


class VirtualTryOnService:
    """Coordinates garment try-on rendering via the YouCam Virtual Try-On API."""

    def __init__(
        self, settings: Settings, client: YouCamClient, upload_service: UploadService
    ) -> None:
        self._settings = settings
        self._client = client
        self._uploads = upload_service

    async def upload_user_image(
        self, content: bytes, content_type: str = "image/jpeg", file_name: str = "person.jpg"
    ) -> str:
        """Upload the person image and return its ``file_id``."""

        result = await self._uploads.upload(
            self._settings.youcam_file_cloth_url, content, content_type, file_name
        )
        return result.file_id

    async def upload_clothing_image(
        self, content: bytes, content_type: str = "image/jpeg", file_name: str = "garment.jpg"
    ) -> str:
        """Upload the garment image and return its ``file_id``."""

        result = await self._uploads.upload(
            self._settings.youcam_file_cloth_url, content, content_type, file_name
        )
        return result.file_id

    async def create_tryon_task(
        self,
        user_file_id: str,
        clothing_file_id: str,
        garment_category: str = DEFAULT_GARMENT_CATEGORY,
        change_shoes: bool = False,
    ) -> str:
        """Create an apparel try-on task and return its ``task_id``."""

        payload = {
            "request_id": 0,
            "payload": {
                "file_sets": {
                    "src_ids": [user_file_id],
                    "ref_ids": [clothing_file_id],
                },
                "actions": [
                    {
                        "id": 0,
                        "params": {
                            "garment_category": garment_category,
                            "change_shoes": change_shoes,
                        },
                    }
                ],
            },
        }
        return await self._client.create_task(self._settings.youcam_task_cloth_url, payload)

    async def poll_tryon(self, task_id: str) -> dict[str, Any]:
        """Poll a try-on task until it reaches a terminal state."""

        return await self._client.poll_task(self._settings.youcam_task_cloth_url, task_id)

    async def generate_tryon(
        self,
        user_image: bytes,
        clothing_image: bytes,
        garment_category: str = DEFAULT_GARMENT_CATEGORY,
        change_shoes: bool = False,
        user_content_type: str = "image/jpeg",
        clothing_content_type: str = "image/jpeg",
    ) -> TryOnResponse:
        """Run the end-to-end virtual try-on workflow and return output images."""

        user_file_id = await self.upload_user_image(user_image, user_content_type)
        clothing_file_id = await self.upload_clothing_image(
            clothing_image, clothing_content_type
        )
        task_id = await self.create_tryon_task(
            user_file_id, clothing_file_id, garment_category, change_shoes
        )
        logger.info(
            "vto.task.created",
            task_id=task_id,
            user_file_id=user_file_id,
            clothing_file_id=clothing_file_id,
        )

        result = await self.poll_tryon(task_id)
        return self._parse_result(task_id, result)

    def _parse_result(self, task_id: str, result: dict[str, Any]) -> TryOnResponse:
        """Extract rendered output image URLs from a successful poll result."""

        urls = collect_urls(result)
        images = [u for u in urls if any(ext in u.lower() for ext in IMAGE_EXTENSIONS)]
        # Fall back to all URLs if none carry a recognised image extension
        # (presigned URLs sometimes omit one).
        output_images = images or urls

        logger.info("vto.result.parsed", task_id=task_id, output_count=len(output_images))
        return TryOnResponse(task_id=task_id, output_images=output_images, raw=result)
