"""Final-answer summarizer.

Turns the accumulated graph state (intent + tool outputs) into the user-facing
reply via Gemini. A single prompt builder feeds both the non-streaming
``summarize`` (used by ``AuraAgent.run``) and the token ``stream`` (used by
``AuraAgent.stream``), so there is one source of truth for the reply prompt.
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from app.agents.llm import ChatLLM, LLMResult
from app.agents.state import AuraState
from app.core.logging import get_logger
from app.prompts.loader import Prompt, load_prompt

logger = get_logger(__name__)


def _dump(obj: Any) -> Any:
    return obj.model_dump() if obj is not None else None


class Summarizer:
    """Composes the final reply from graph state."""

    def __init__(self, llm: ChatLLM) -> None:
        self._llm = llm

    def _build(self, state: AuraState) -> tuple[str, str]:
        system = f"{load_prompt(Prompt.SYSTEM)}\n\n{load_prompt(Prompt.STYLIST)}"
        history = state.get("history") or []
        context = {
            "user_message": state.get("message", ""),
            "intent": getattr(state.get("intent"), "value", str(state.get("intent"))),
            "executed_tools": state.get("executed_tools", []),
            "skin_analysis": _dump(state.get("skin_analysis")),
            "color_palette": _dump(state.get("color_palette")),
            "try_on": _dump(state.get("try_on")),
            "recommendations": _dump(state.get("recommendations")),
            "recent_history": [f"{m.role}: {m.content}" for m in history[-6:]],
        }
        prompt = (
            "Compose the reply to the user using only this context.\n\n"
            f"CONTEXT:\n{json.dumps(context, indent=2, ensure_ascii=False)}"
        )
        return system, prompt

    async def summarize(self, state: AuraState) -> LLMResult:
        system, prompt = self._build(state)
        result = await self._llm.complete(system=system, prompt=prompt)
        logger.info("summarizer.done", total_tokens=result.usage.total_tokens)
        return result

    async def stream(self, state: AuraState) -> AsyncIterator[str]:
        system, prompt = self._build(state)
        async for token in self._llm.stream(system=system, prompt=prompt):
            yield token
