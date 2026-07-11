"""Schemas for the apparel virtual try-on domain."""

from pydantic import Field

from app.schemas.common import APIModel


class TryOnResponse(APIModel):
    """Parsed result of a completed apparel virtual try-on task."""

    task_id: str
    output_images: list[str] = Field(default_factory=list)
    raw: dict[str, object] = Field(default_factory=dict)
