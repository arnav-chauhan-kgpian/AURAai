"""Recommendation service.

Synthesises skin scores, color palette, Fitzpatrick type, try-on output and
conversation history into skincare, outfit, color and shopping recommendations.
It prompts Gemini with a structured context and returns a validated
:class:`RecommendationSet` — the reasoning lives here, not in the agent graph.
"""

import json

from app.agents.llm import ChatLLM
from app.config.config import Settings
from app.core.logging import get_logger
from app.prompts.loader import Prompt, load_prompt
from app.schemas.recommendation import RecommendationContext, RecommendationSet

logger = get_logger(__name__)


class RecommendationService:
    """Produces stylist recommendations from analysis signals via Gemini."""

    def __init__(self, settings: Settings, llm: ChatLLM) -> None:
        self._settings = settings
        self._llm = llm

    async def build(self, context: RecommendationContext) -> RecommendationSet:
        """Generate a grouped recommendation set from the available signals."""

        system = "\n\n".join(
            (
                load_prompt(Prompt.SYSTEM),
                load_prompt(Prompt.SKIN),
                load_prompt(Prompt.FASHION),
            )
        )
        prompt = self._render_prompt(context)

        result = await self._llm.structured(
            system=system, prompt=prompt, schema=RecommendationSet
        )
        logger.info(
            "recommendation.built",
            intent=context.intent,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
            skincare=len(result.value.skincare),
            outfit=len(result.value.outfit),
        )
        return result.value

    @staticmethod
    def _render_prompt(context: RecommendationContext) -> str:
        payload = {
            "user_message": context.message,
            "intent": context.intent,
            "skin_scores": [s.model_dump() for s in context.skin_scores],
            "color_palette": context.color_palette.model_dump()
            if context.color_palette
            else None,
            "fitzpatrick_type": context.fitzpatrick_type,
            "try_on_images": context.try_on_images,
            "preferred_style": context.preferred_style,
            "recent_history": context.history,
        }
        return (
            "Generate recommendations for this user using only the context below.\n"
            "Populate skincare, outfit, colors and shopping as warranted by the "
            "signals; leave a group empty if there is no basis for it.\n\n"
            f"CONTEXT:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
        )
