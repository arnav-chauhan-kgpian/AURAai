"""Shared schema primitives used across request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    """Base model with shared serialisation configuration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ImageRef(APIModel):
    """Reference to an image asset either by remote URL or storage id."""

    url: str | None = None
    storage_id: str | None = None


class TaskStatus(APIModel):
    """Status envelope for a long-running upstream task."""

    task_id: str
    status: str = Field(description="One of: pending, running, success, error")
    created_at: datetime | None = None
