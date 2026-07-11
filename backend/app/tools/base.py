"""Common tool interface.

Every agent capability is an :class:`AuraTool`. The base class provides the
template method ``run`` — it times the call, logs it (tool, status, latency),
and converts unexpected errors into an ``error`` result — so concrete tools only
implement ``_execute`` and never duplicate that boilerplate. Tools report their
effect on the graph via ``ToolResult.updates`` (a partial state patch) rather
than mutating shared state.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Any, ClassVar

from app.core.logging import get_logger
from app.schemas.agent import AgentImages, Intent

logger = get_logger(__name__)


class ToolStatus(str, Enum):
    """Outcome of a tool execution."""

    OK = "ok"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ToolResult:
    """The outcome of running a tool and its effect on graph state."""

    tool: str
    status: ToolStatus
    note: str | None = None
    latency_ms: float = 0.0
    updates: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        """A log/response-friendly view (without the state patch)."""

        return {
            "tool": self.tool,
            "status": self.status.value,
            "note": self.note,
            "latency_ms": self.latency_ms,
        }


@dataclass
class ToolRunContext:
    """Runtime inputs available to a tool during a turn."""

    session_id: str
    message: str
    intent: Intent
    images: AgentImages
    state: dict[str, Any]  # current merged AuraState view (read-only for tools)


class AuraTool(ABC):
    """Base class for every agent tool."""

    name: ClassVar[str]
    description: ClassVar[str]

    async def run(self, ctx: ToolRunContext) -> ToolResult:
        """Execute the tool with timing, logging and error containment."""

        start = perf_counter()
        try:
            result = await self._execute(ctx)
        except Exception as exc:  # noqa: BLE001 - surface as a result, not a crash
            latency = round((perf_counter() - start) * 1000, 1)
            logger.warning(
                "tool.error", tool=self.name, latency_ms=latency, error=str(exc)
            )
            return ToolResult(self.name, ToolStatus.ERROR, note=str(exc), latency_ms=latency)

        result.latency_ms = round((perf_counter() - start) * 1000, 1)
        logger.info(
            "tool.executed",
            tool=self.name,
            status=result.status.value,
            latency_ms=result.latency_ms,
            note=result.note,
        )
        return result

    @abstractmethod
    async def _execute(self, ctx: ToolRunContext) -> ToolResult:
        """Perform the tool's work and return a result with any state updates."""

    # --- Result builders (shared by concrete tools) ----------------------

    def ok(self, updates: dict[str, Any], note: str | None = None) -> ToolResult:
        return ToolResult(self.name, ToolStatus.OK, note=note, updates=updates)

    def skipped(self, note: str) -> ToolResult:
        return ToolResult(self.name, ToolStatus.SKIPPED, note=note)
