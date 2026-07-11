"""Agent planner.

Classifies a user request into one of the :class:`Intent` categories. This is
what makes AuraAI decide *which* capabilities to use — the user never names an
API. The planner asks Gemini for a structured classification and falls back to a
transparent keyword heuristic if the model is unavailable, so routing is always
deterministic and testable.
"""

from app.agents.llm import ChatLLM
from app.core.logging import get_logger
from app.prompts.loader import Prompt, load_prompt
from app.schemas.agent import Intent, IntentClassification

logger = get_logger(__name__)

_SKIN_TERMS = (
    "skin",
    "acne",
    "oily",
    "dry",
    "pore",
    "wrinkle",
    "redness",
    "breakout",
    "complexion",
    "blemish",
    "spot",
)
_STYLE_TERMS = (
    "wear",
    "outfit",
    "color",
    "colour",
    "style",
    "fashion",
    "dress",
    "look",
    "clothes",
    "wardrobe",
)
_TRYON_TERMS = ("try", "try on", "try-on", "how would", "look on me", "fit me")


class Planner:
    """Routes requests to intents via structured LLM classification."""

    def __init__(self, llm: ChatLLM) -> None:
        self._llm = llm

    async def classify(
        self,
        message: str,
        *,
        history: list[str] | None = None,
        has_face_image: bool = False,
        has_garment_image: bool = False,
    ) -> IntentClassification:
        """Classify a message into an intent, with a keyword fallback."""

        prompt = self._render_prompt(message, history or [], has_face_image, has_garment_image)
        try:
            result = await self._llm.structured(
                system=load_prompt(Prompt.PLANNER),
                prompt=prompt,
                schema=IntentClassification,
            )
            logger.info(
                "planner.classified",
                intent=result.value.intent.value,
                total_tokens=result.usage.total_tokens,
                source="llm",
            )
            return result.value
        except Exception as exc:  # noqa: BLE001 - never let routing hard-fail
            logger.warning("planner.llm_failed", error=str(exc))
            classification = self._rule_based(message, has_garment_image)
            logger.info(
                "planner.classified", intent=classification.intent.value, source="fallback"
            )
            return classification

    @staticmethod
    def _render_prompt(
        message: str, history: list[str], has_face: bool, has_garment: bool
    ) -> str:
        history_block = "\n".join(f"- {line}" for line in history[-6:]) or "(none)"
        return (
            f"USER MESSAGE:\n{message}\n\n"
            f"RECENT HISTORY:\n{history_block}\n\n"
            f"ATTACHMENTS: face_image={has_face}, garment_image={has_garment}\n\n"
            "Classify the intent."
        )

    @staticmethod
    def _rule_based(message: str, has_garment_image: bool) -> IntentClassification:
        text = message.lower()
        has_skin = any(term in text for term in _SKIN_TERMS)
        has_style = any(term in text for term in _STYLE_TERMS)
        wants_tryon = has_garment_image or any(term in text for term in _TRYON_TERMS)

        if has_skin and has_style:
            intent = Intent.SKIN_AND_STYLE
        elif wants_tryon and not has_skin:
            intent = Intent.TRYON_ONLY
        elif has_skin:
            intent = Intent.SKIN_ONLY
        elif has_style:
            intent = Intent.STYLE_ONLY
        elif text.strip():
            intent = Intent.CHAT_ONLY
        else:
            intent = Intent.UNKNOWN

        return IntentClassification(
            intent=intent,
            rationale="Keyword heuristic (LLM unavailable).",
            wants_tryon=wants_tryon,
        )
