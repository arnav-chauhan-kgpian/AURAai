"""Chat LLM abstraction.

A narrow interface over a chat model so the agent, planner, summarizer and
recommendation service depend on a capability — not on a concrete SDK. The
Gemini implementation lives in ``app.services.gemini_client``; tests inject a
fake. This is what makes "mock Gemini" straightforward.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class TokenUsage:
    """Token accounting for a single LLM call."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    @classmethod
    def from_metadata(cls, metadata: dict[str, int] | None) -> "TokenUsage":
        data = metadata or {}
        inp = int(data.get("input_tokens", 0))
        out = int(data.get("output_tokens", 0))
        return cls(
            input_tokens=inp,
            output_tokens=out,
            total_tokens=int(data.get("total_tokens", inp + out)),
        )


@dataclass
class LLMResult:
    """The text result of a completion plus its token usage."""

    text: str
    usage: TokenUsage = field(default_factory=TokenUsage)


@dataclass
class StructuredResult(Generic[T]):
    """A parsed structured output plus the token usage of the call."""

    value: T
    usage: TokenUsage = field(default_factory=TokenUsage)


@runtime_checkable
class ChatLLM(Protocol):
    """Capability a chat model must provide to power the agent."""

    model_name: str

    async def complete(self, *, system: str, prompt: str) -> LLMResult:
        """Return a full (non-streaming) completion."""
        ...

    async def structured(self, *, system: str, prompt: str, schema: type[T]) -> StructuredResult[T]:
        """Return a validated instance of ``schema`` via structured output."""
        ...

    def stream(self, *, system: str, prompt: str) -> AsyncIterator[str]:
        """Yield text chunks as they are generated."""
        ...
