"""Final-answer summarizer.

Turns the accumulated graph state (intent + tool outputs) into the user-facing
reply via the LLM. A single prompt builder feeds both the non-streaming
``summarize`` and the token ``stream``.

Two adaptations to a token-constrained LLM tier: the context sent to the model is
**compact** (no raw provider envelopes or long signed URLs — only the fields the
reply needs), and on any LLM failure the reply **falls back** to a deterministic
summary built from results, so a turn never hard-fails.
"""

from collections.abc import AsyncIterator

from app.agents.llm import ChatLLM, LLMResult
from app.agents.state import AuraState
from app.core.logging import get_logger
from app.prompts.loader import Prompt, load_prompt

logger = get_logger(__name__)


def _humanize(token: str) -> str:
    return token.replace("_", " ").strip().title()


def _compact_context(state: AuraState) -> str:
    """A minimal, token-frugal view of the results for the reply prompt."""

    lines: list[str] = [
        f"User message: {state.get('message', '')}",
        f"Intent: {getattr(state.get('intent'), 'value', state.get('intent'))}",
    ]

    skin = state.get("skin_analysis")
    if skin is not None and skin.scores:
        top = sorted(skin.scores, key=lambda s: s.ui_score, reverse=True)[:4]
        lines.append(
            "Skin (0-100, higher = more pronounced): "
            + ", ".join(f"{_humanize(s.concern)} {round(s.ui_score)}" for s in top)
        )

    palette = state.get("color_palette")
    if palette is not None:
        lines.append(
            f"Palette: {palette.season}, {palette.undertone} undertone; "
            f"wear {', '.join(palette.recommended_colors[:5])}; "
            f"avoid {', '.join(palette.avoid_colors[:3])}"
        )

    recs = state.get("recommendations")
    if recs is not None:
        if recs.skincare:
            lines.append("Skincare: " + "; ".join(r.title for r in recs.skincare[:4]))
        if recs.outfit:
            lines.append("Outfit: " + "; ".join(r.title for r in recs.outfit[:4]))
        if recs.colors:
            lines.append("Colors: " + ", ".join(recs.colors[:6]))

    if state.get("try_on") is not None:
        lines.append("A virtual try-on image was rendered (shown to the user).")

    history = state.get("history") or []
    if history:
        recent = "; ".join(f"{m.role}: {m.content[:120]}" for m in history[-3:])
        lines.append(f"Recent history: {recent}")

    return "\n".join(lines)


def _fallback_reply(state: AuraState) -> str:
    """A grounded reply composed without the LLM (used on LLM failure)."""

    parts: list[str] = []
    skin = state.get("skin_analysis")
    if skin is not None and skin.scores:
        top = sorted(skin.scores, key=lambda s: s.ui_score, reverse=True)[:3]
        parts.append(
            "Your main skin focus areas are "
            + ", ".join(f"{_humanize(s.concern)} ({round(s.ui_score)})" for s in top)
            + "."
        )
    palette = state.get("color_palette")
    if palette is not None:
        parts.append(
            f"Your colors read {palette.season} with a {palette.undertone} undertone — "
            f"lean into {', '.join(palette.recommended_colors[:4])}."
        )
    recs = state.get("recommendations")
    if recs is not None and recs.summary:
        parts.append(recs.summary)
    if state.get("try_on") is not None:
        parts.append("Your virtual try-on is ready below.")

    if not parts:
        return (
            "I'm here to help with your skin and style — tell me a bit about your "
            "skin concerns or the look you're going for and I'll take it from there."
        )
    return " ".join(parts)


class Summarizer:
    """Composes the final reply from graph state."""

    def __init__(self, llm: ChatLLM) -> None:
        self._llm = llm

    def _build(self, state: AuraState) -> tuple[str, str]:
        system = f"{load_prompt(Prompt.SYSTEM)}\n\n{load_prompt(Prompt.STYLIST)}"
        prompt = (
            "Compose the reply to the user using only this context.\n\n"
            f"CONTEXT:\n{_compact_context(state)}"
        )
        return system, prompt

    async def summarize(self, state: AuraState) -> LLMResult:
        system, prompt = self._build(state)
        try:
            result = await self._llm.complete(system=system, prompt=prompt)
            logger.info("summarizer.done", total_tokens=result.usage.total_tokens)
            return result
        except Exception as exc:  # noqa: BLE001 - degrade gracefully, never 500 the turn
            logger.warning("summarizer.fallback", error=str(exc))
            return LLMResult(text=_fallback_reply(state))

    async def stream(self, state: AuraState) -> AsyncIterator[str]:
        system, prompt = self._build(state)
        streamed = False
        try:
            async for token in self._llm.stream(system=system, prompt=prompt):
                streamed = True
                yield token
        except Exception as exc:  # noqa: BLE001
            logger.warning("summarizer.stream_fallback", error=str(exc))
        if not streamed:
            yield _fallback_reply(state)
