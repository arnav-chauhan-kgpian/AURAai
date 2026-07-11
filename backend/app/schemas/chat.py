"""Schemas for the conversational agent interface."""

from typing import Literal

from pydantic import Field

from app.schemas.color import ColorPalette
from app.schemas.common import APIModel
from app.schemas.recommendation import RecommendationSet
from app.schemas.skin import SkinAnalysisResponse
from app.schemas.vto import TryOnResponse


class ChatMessage(APIModel):
    """A single turn in a conversation."""

    role: Literal["user", "assistant", "system"]
    content: str


class ChatResponse(APIModel):
    """Agent reply for a turn, with the structured artifacts it produced."""

    session_id: str
    reply: str
    intent: str
    tools_used: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    recommendations: RecommendationSet | None = None
    skin_analysis: SkinAnalysisResponse | None = None
    try_on: TryOnResponse | None = None
    color_palette: ColorPalette | None = None
