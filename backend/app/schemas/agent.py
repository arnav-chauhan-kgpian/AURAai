"""Schemas for the autonomous agent: intents, inputs and streaming events."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import APIModel


class Intent(str, Enum):
    """The intent categories the planner routes requests into."""

    SKIN_ONLY = "SKIN_ONLY"
    TRYON_ONLY = "TRYON_ONLY"
    STYLE_ONLY = "STYLE_ONLY"
    SKIN_AND_STYLE = "SKIN_AND_STYLE"
    CHAT_ONLY = "CHAT_ONLY"
    UNKNOWN = "UNKNOWN"


class IntentClassification(APIModel):
    """Structured output of the planner's intent classification."""

    intent: Intent
    rationale: str = Field(description="One sentence explaining the routing decision")
    wants_tryon: bool = False
    garment_category: str | None = None


class AgentImages(BaseModel):
    """Binary image inputs for a turn.

    Carried through the graph state but never persisted to memory. ``bytes`` is
    permitted via ``arbitrary_types_allowed``.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    face_image: bytes | None = None
    face_content_type: str = "image/jpeg"
    garment_image: bytes | None = None
    garment_content_type: str = "image/jpeg"
    garment_category: str = "upper_body"

    @property
    def has_face(self) -> bool:
        return self.face_image is not None

    @property
    def has_garment(self) -> bool:
        return self.garment_image is not None


class AgentStreamEvent(BaseModel):
    """A single event emitted while streaming an agent run."""

    type: Literal["intent", "step", "tool", "token", "final", "error"]
    data: dict[str, object] = Field(default_factory=dict)
