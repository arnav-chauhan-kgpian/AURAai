"""Groq implementation of the :class:`ChatLLM` interface.

Wraps ``langchain-groq``'s ``ChatGroq`` (fast Llama-class inference) and adapts it
to the app's narrow LLM capability: text completion, validated structured output,
and token streaming. Interchangeable with the Gemini implementation — the agent,
planner and recommendation service are provider-agnostic.
"""

from collections.abc import AsyncIterator

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.agents.llm import LLMResult, StructuredResult, T, TokenUsage
from app.config.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroqChatModel:
    """A :class:`ChatLLM` backed by Groq."""

    def __init__(self, settings: Settings) -> None:
        self.model_name = settings.groq_model
        self._model = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key or None,
            temperature=0.4,
        )

    @staticmethod
    def _messages(system: str, prompt: str) -> list[object]:
        return [SystemMessage(content=system), HumanMessage(content=prompt)]

    @staticmethod
    def _usage(message: object) -> TokenUsage:
        metadata = getattr(message, "usage_metadata", None)
        return TokenUsage.from_metadata(metadata if isinstance(metadata, dict) else None)

    async def complete(self, *, system: str, prompt: str) -> LLMResult:
        message = await self._model.ainvoke(self._messages(system, prompt))
        usage = self._usage(message)
        logger.info("groq.complete", model=self.model_name, total_tokens=usage.total_tokens)
        return LLMResult(text=str(message.content), usage=usage)

    async def structured(
        self, *, system: str, prompt: str, schema: type[T]
    ) -> StructuredResult[T]:
        runnable = self._model.with_structured_output(schema, include_raw=True)
        output = await runnable.ainvoke(self._messages(system, prompt))
        parsed: BaseModel = output["parsed"]
        usage = self._usage(output.get("raw"))
        logger.info(
            "groq.structured",
            model=self.model_name,
            schema=schema.__name__,
            total_tokens=usage.total_tokens,
        )
        return StructuredResult(value=parsed, usage=usage)  # type: ignore[arg-type]

    async def stream(self, *, system: str, prompt: str) -> AsyncIterator[str]:
        async for chunk in self._model.astream(self._messages(system, prompt)):
            content = getattr(chunk, "content", "")
            if content:
                yield str(content)
