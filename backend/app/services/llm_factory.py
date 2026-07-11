"""LLM provider selection.

Returns the configured :class:`ChatLLM` implementation (Groq or Gemini) based on
``resolved_llm_provider``. Provider modules are imported lazily so the app only
depends on the SDK it actually uses.
"""

from app.agents.llm import ChatLLM
from app.config.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def build_llm(settings: Settings) -> ChatLLM | None:
    """Construct the active LLM, or ``None`` if no provider is configured."""

    provider = settings.resolved_llm_provider

    if provider == "groq":
        from app.services.groq_client import GroqChatModel

        logger.info("llm.provider_selected", provider="groq", model=settings.groq_model)
        return GroqChatModel(settings)

    if provider == "gemini":
        from app.services.gemini_client import GeminiChatModel

        logger.info("llm.provider_selected", provider="gemini", model=settings.gemini_model)
        return GeminiChatModel(settings)

    return None
