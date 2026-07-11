"""Domain models.

Persistence-facing entities that map to Supabase tables. These are distinct from
the transport schemas in ``app.schemas`` so the storage representation can evolve
independently of the public API contract.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Entity(BaseModel):
    """Base persistence entity."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class Session(Entity):
    """A user's stylist session."""

    user_id: str | None = None


class AnalysisRecord(Entity):
    """A stored skin analysis result associated with a session."""

    session_id: str
    overall_score: float
