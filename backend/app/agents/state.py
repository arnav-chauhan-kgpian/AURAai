"""Agent graph state.

The typed state threaded through the LangGraph nodes. It is a plain ``TypedDict``
(no LLM-library coupling) so it is trivially serialisable and testable. The graph
is linear, so nodes return partial updates that are merged by key.
"""

from typing import Any, TypedDict

from app.schemas.agent import AgentImages, Intent
from app.schemas.chat import ChatMessage
from app.schemas.color import ColorPalette
from app.schemas.recommendation import RecommendationSet
from app.schemas.skin import SkinAnalysisResponse
from app.schemas.vto import TryOnResponse


class AuraState(TypedDict, total=False):
    """State shared across the AuraAgent graph nodes."""

    # --- Inputs -----------------------------------------------------------
    session_id: str
    message: str
    images: AgentImages

    # --- Planning ---------------------------------------------------------
    intent: Intent
    intent_rationale: str

    # --- Execution bookkeeping -------------------------------------------
    current_step: str
    executed_tools: list[str]
    tool_outputs: dict[str, dict[str, Any]]
    retry_count: int

    # --- Memory context ---------------------------------------------------
    history: list[ChatMessage]
    profile: dict[str, Any]

    # --- Tool results -----------------------------------------------------
    skin_analysis: SkinAnalysisResponse | None
    try_on: TryOnResponse | None
    color_palette: ColorPalette | None
    recommendations: RecommendationSet | None

    # --- Output -----------------------------------------------------------
    conversation_summary: str
    final_response: str


def initial_state(
    session_id: str, message: str, images: AgentImages
) -> AuraState:
    """Build a fresh state for a turn."""

    return AuraState(
        session_id=session_id,
        message=message,
        images=images,
        intent=Intent.UNKNOWN,
        intent_rationale="",
        current_step="start",
        executed_tools=[],
        tool_outputs={},
        retry_count=0,
        history=[],
        profile={},
        skin_analysis=None,
        try_on=None,
        color_palette=None,
        recommendations=None,
        conversation_summary="",
        final_response="",
    )
