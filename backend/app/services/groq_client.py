"""Groq implementation of the :class:`ChatLLM` interface.

Wraps ``langchain-groq``'s ``ChatGroq`` (fast Llama-class inference) and adapts it
to the app's narrow LLM capability: text completion, validated structured output,
and token streaming. Interchangeable with the Gemini implementation — the agent,
planner and recommendation service are provider-agnostic.
"""

import asyncio
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

    def __init__(self, settings: Settings, model: str | None = None) -> None:
        self.model_name = model or settings.groq_model
        self._model = ChatGroq(
            model=self.model_name,
            api_key=settings.groq_api_key or None,
            temperature=0.4,
            # Cap output so no single call blows the token budget.
            max_tokens=settings.groq_max_tokens,
            # Auto-retry (honoring Groq's Retry-After) so transient 429/TPM
            # bursts under concurrency degrade to a retry, not a 500.
            max_retries=3,
        )
        # Gate concurrent calls so bursts queue instead of hitting the TPM
        # window all at once (a process-wide limit — the model is a singleton).
        self._sem = asyncio.Semaphore(settings.groq_max_concurrency)

    @staticmethod
    def _messages(system: str, prompt: str) -> list[object]:
        return [SystemMessage(content=system), HumanMessage(content=prompt)]

    @staticmethod
    def _usage(message: object) -> TokenUsage:
        metadata = getattr(message, "usage_metadata", None)
        return TokenUsage.from_metadata(metadata if isinstance(metadata, dict) else None)

    async def complete(self, *, system: str, prompt: str) -> LLMResult:
        async with self._sem:
            message = await self._model.ainvoke(self._messages(system, prompt))
        usage = self._usage(message)
        logger.info("groq.complete", model=self.model_name, total_tokens=usage.total_tokens)
        return LLMResult(text=str(message.content), usage=usage)

    async def structured(
        self, *, system: str, prompt: str, schema: type[T]
    ) -> StructuredResult[T]:
        runnable = self._model.with_structured_output(schema, include_raw=True)
        async with self._sem:
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
        async with self._sem:
            async for chunk in self._model.astream(self._messages(system, prompt)):
                content = getattr(chunk, "content", "")
                if content:
                    yield str(content)
