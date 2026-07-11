"""Skin analysis tool.

Exposes the skin analysis service to the agent. Skips cleanly when no face image
is attached so the graph never hard-fails on missing input.
"""

from typing import ClassVar

from app.services.skin_service import SkinService
from app.tools.base import AuraTool, ToolResult, ToolRunContext


class SkinAnalysisTool(AuraTool):
    """Analyze the user's facial skin and produce concern scores."""

    name: ClassVar[str] = "skin_analysis"
    description: ClassVar[str] = "Analyze facial skin and return scored concerns (0-100)."

    def __init__(self, skin_service: SkinService) -> None:
        self._service = skin_service

    async def _execute(self, ctx: ToolRunContext) -> ToolResult:
        images = ctx.images
        if not images.has_face:
            return self.skipped("No face image provided; skipping skin analysis.")

        result = await self._service.analyze(
            image=images.face_image,  # type: ignore[arg-type]
            content_type=images.face_content_type,
        )
        return self.ok(
            {"skin_analysis": result}, note=f"Scored {len(result.scores)} skin concerns."
        )
