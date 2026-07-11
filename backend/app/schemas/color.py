"""Schemas for color analysis."""

from pydantic import Field

from app.schemas.common import APIModel


class ColorPalette(APIModel):
    """A personalised color palette derived from skin tone / Fitzpatrick type."""

    fitzpatrick_type: str
    undertone: str = Field(description="warm, cool or neutral")
    season: str = Field(description="Seasonal color analysis label, e.g. 'Autumn'")
    recommended_colors: list[str] = Field(default_factory=list)
    avoid_colors: list[str] = Field(default_factory=list)
    rationale: str = ""
