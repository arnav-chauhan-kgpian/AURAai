"""Schemas for stylist recommendations."""

from pydantic import Field

from app.schemas.color import ColorPalette
from app.schemas.common import APIModel
from app.schemas.skin import SkinScore


class ProductRecommendation(APIModel):
    """A single recommended product type or routine step."""

    title: str
    category: str
    rationale: str
    url: str | None = None


class RecommendationSet(APIModel):
    """A grouped set of recommendations produced by the agent."""

    summary: str = ""
    skincare: list[ProductRecommendation] = Field(default_factory=list)
    outfit: list[ProductRecommendation] = Field(default_factory=list)
    colors: list[str] = Field(
        default_factory=list,
        description="A flat array of color name strings, e.g. ['olive','navy']. Not an object.",
    )
    shopping: list[ProductRecommendation] = Field(default_factory=list)


class RecommendationContext(APIModel):
    """Structured inputs the recommendation service reasons over."""

    message: str
    intent: str
    skin_scores: list[SkinScore] = Field(default_factory=list)
    color_palette: ColorPalette | None = None
    fitzpatrick_type: str | None = None
    try_on_images: list[str] = Field(default_factory=list)
    history: list[str] = Field(default_factory=list)
    preferred_style: str | None = None
