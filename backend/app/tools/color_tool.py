"""Color palette tool.

Derives a personalised color palette from the current skin analysis (if present)
or the user's stored Fitzpatrick type via the deterministic color service.
"""

from typing import ClassVar

from app.services.color_service import ColorService
from app.tools.base import AuraTool, ToolResult, ToolRunContext


class ColorPaletteTool(AuraTool):
    """Produce a personalised color palette from skin tone signals."""

    name: ClassVar[str] = "color_palette"
    description: ClassVar[str] = "Derive flattering colors from skin tone / Fitzpatrick type."

    def __init__(self, color_service: ColorService) -> None:
        self._service = color_service

    async def _execute(self, ctx: ToolRunContext) -> ToolResult:
        profile = ctx.state.get("profile") or {}
        palette = self._service.derive(
            skin_analysis=ctx.state.get("skin_analysis"),
            fitzpatrick_type=profile.get("fitzpatrick_type") or profile.get("skin_type"),
        )
        return self.ok(
            {"color_palette": palette}, note=f"{palette.season} palette ({palette.undertone})."
        )
