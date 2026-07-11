"""Schemas for the skin analysis domain."""

from pydantic import Field

from app.schemas.common import APIModel


class SkinScore(APIModel):
    """A single skin concern with its measured severity.

    YouCam reports scores on a 0–100 scale and distinguishes the raw engine
    output (``raw_score``) from the UI-adjusted value (``ui_score``).
    """

    concern: str
    raw_score: float
    ui_score: float


class OverlayImage(APIModel):
    """A visual overlay (mask) image produced for a given concern."""

    concern: str
    url: str


class SkinAnalysisResponse(APIModel):
    """Parsed result of a completed skin analysis task."""

    task_id: str
    scores: list[SkinScore] = Field(default_factory=list)
    overlays: list[OverlayImage] = Field(default_factory=list)
    raw: dict[str, object] = Field(default_factory=dict)
