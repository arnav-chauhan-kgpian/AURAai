"""Recommendation tool.

Exposes the recommendation service to the agent, assembling a structured context
from whatever signals earlier tools produced (skin, color, try-on, history).
"""

from typing import ClassVar

from app.schemas.recommendation import RecommendationContext
from app.services.recommendation_service import RecommendationService
from app.tools.base import AuraTool, ToolResult, ToolRunContext


class RecommendationTool(AuraTool):
    """Synthesise skincare, outfit, color and shopping recommendations."""

    name: ClassVar[str] = "recommendation"
    description: ClassVar[str] = "Generate skincare, outfit, color and shopping advice."

    def __init__(self, recommendation_service: RecommendationService) -> None:
        self._service = recommendation_service

    async def _execute(self, ctx: ToolRunContext) -> ToolResult:
        state = ctx.state
        skin = state.get("skin_analysis")
        palette = state.get("color_palette")
        try_on = state.get("try_on")
        profile = state.get("profile") or {}
        history = state.get("history") or []

        context = RecommendationContext(
            message=ctx.message,
            intent=ctx.intent.value,
            skin_scores=list(skin.scores) if skin else [],
            color_palette=palette,
            fitzpatrick_type=(
                palette.fitzpatrick_type if palette else profile.get("fitzpatrick_type")
            ),
            try_on_images=list(try_on.output_images) if try_on else [],
            history=[f"{m.role}: {m.content}" for m in history[-6:]],
            preferred_style=profile.get("preferred_style"),
        )
        recommendations = await self._service.build(context)
        count = len(recommendations.skincare) + len(recommendations.outfit)
        return self.ok({"recommendations": recommendations}, note=f"{count} recommendations.")
