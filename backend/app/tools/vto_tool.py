"""Virtual try-on tool.

Exposes the apparel virtual try-on service to the agent. Requires both a person
photo and a garment image; skips cleanly otherwise.
"""

from typing import ClassVar

from app.services.vto_service import VirtualTryOnService
from app.tools.base import AuraTool, ToolResult, ToolRunContext


class VirtualTryOnTool(AuraTool):
    """Render a garment onto the user's photo."""

    name: ClassVar[str] = "virtual_try_on"
    description: ClassVar[str] = "Render a specific garment on the user's photo."

    def __init__(self, vto_service: VirtualTryOnService) -> None:
        self._service = vto_service

    async def _execute(self, ctx: ToolRunContext) -> ToolResult:
        images = ctx.images
        if not images.has_face or not images.has_garment:
            return self.skipped(
                "Need both a person photo and a garment image to run try-on."
            )

        result = await self._service.generate_tryon(
            user_image=images.face_image,  # type: ignore[arg-type]
            clothing_image=images.garment_image,  # type: ignore[arg-type]
            garment_category=images.garment_category,
            user_content_type=images.face_content_type,
            clothing_content_type=images.garment_content_type,
        )
        return self.ok(
            {"try_on": result}, note=f"Rendered {len(result.output_images)} try-on image(s)."
        )
