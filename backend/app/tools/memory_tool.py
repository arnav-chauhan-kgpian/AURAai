"""Conversation memory tool.

Wraps :class:`ConversationMemory` behind the common tool interface. Its
``recall`` method loads prior context at the start of a turn; its ``run`` (the
common interface) persists the completed turn — history, the latest
skin/try-on/color snapshot, and any learned profile updates.
"""

from typing import Any, ClassVar

from app.agents.memory import ConversationMemory, MemoryContext
from app.schemas.chat import ChatMessage
from app.tools.base import AuraTool, ToolResult, ToolRunContext


class ConversationMemoryTool(AuraTool):
    """Recall and persist conversation memory for a session."""

    name: ClassVar[str] = "conversation_memory"
    description: ClassVar[str] = "Recall prior context and persist the latest turn."

    def __init__(self, memory: ConversationMemory) -> None:
        self._memory = memory

    async def recall(self, session_id: str) -> MemoryContext:
        """Load history, latest snapshot and durable profile for a session."""

        return await self._memory.recall(session_id)

    async def _execute(self, ctx: ToolRunContext) -> ToolResult:
        state = ctx.state
        user_message = ChatMessage(role="user", content=ctx.message)
        assistant_message = ChatMessage(role="assistant", content=state.get("final_response", ""))

        await self._memory.persist(
            ctx.session_id,
            user_message=user_message,
            assistant_message=assistant_message,
            skin_analysis=state.get("skin_analysis"),
            try_on=state.get("try_on"),
            color_palette=state.get("color_palette"),
            recommendations=state.get("recommendations"),
            profile_updates=self._derive_profile_updates(state),
        )
        return self.ok({}, note="Persisted turn to memory.")

    @staticmethod
    def _derive_profile_updates(state: dict[str, Any]) -> dict[str, Any]:
        """Learn durable preferences from this turn's results."""

        updates: dict[str, Any] = {}
        palette = state.get("color_palette")
        if palette is not None:
            updates["fitzpatrick_type"] = palette.fitzpatrick_type
            updates["favorite_colors"] = list(palette.recommended_colors[:5])
        skin = state.get("skin_analysis")
        if skin is not None and skin.scores:
            top = max(skin.scores, key=lambda s: s.ui_score)
            updates["skin_type"] = top.concern
        return updates
