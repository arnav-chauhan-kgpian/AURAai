"""AuraAgent — the autonomous skin & style agent.

Assembles the planner, tool registry, memory and summarizer into a LangGraph
workflow and exposes two entrypoints the API layer calls:

* :meth:`run` — execute the full graph and return a :class:`ChatResponse`.
* :meth:`stream` — reuse the same node logic but stream the final reply token by
  token.

The graph nodes are methods on this class; the graph wiring lives in
``app.workflows.aura_graph``. Endpoints contain no business logic — they only
build the request and ``await agent.run(...)`` / iterate ``agent.stream(...)``.
"""

from collections.abc import AsyncIterator
from time import perf_counter
from typing import Any

from app.agents.planner import Planner
from app.agents.state import AuraState, initial_state
from app.agents.summarizer import Summarizer
from app.agents.tool_registry import ToolRegistry
from app.config.config import Settings
from app.core.logging import get_logger
from app.schemas.agent import AgentImages, AgentStreamEvent, Intent
from app.schemas.chat import ChatResponse
from app.tools.base import ToolRunContext
from app.tools.memory_tool import ConversationMemoryTool

logger = get_logger(__name__)

_DOMAIN_KEYS = ("skin_analysis", "color_palette", "try_on", "recommendations")


class AuraAgent:
    """Autonomous agent that decides which tools to run for each request."""

    def __init__(
        self,
        *,
        settings: Settings,
        planner: Planner,
        registry: ToolRegistry,
        memory_tool: ConversationMemoryTool,
        summarizer: Summarizer,
    ) -> None:
        self._settings = settings
        self._planner = planner
        self._registry = registry
        self._memory_tool = memory_tool
        self._summarizer = summarizer
        # Imported here to avoid a module-level cycle (graph imports the agent).
        from app.workflows.aura_graph import build_aura_graph

        self._graph = build_aura_graph(self)

    # --- Graph nodes ------------------------------------------------------

    async def detect_intent(self, state: AuraState) -> dict[str, Any]:
        """Load memory and classify the request into an intent."""

        images: AgentImages = state["images"]
        context = await self._memory_tool.recall(state["session_id"])
        classification = await self._planner.classify(
            state["message"],
            history=context.history_lines(),
            has_face_image=images.has_face,
            has_garment_image=images.has_garment,
        )
        logger.info(
            "agent.intent_detected",
            session_id=state["session_id"],
            intent=classification.intent.value,
            rationale=classification.rationale,
        )
        return {
            "intent": classification.intent,
            "intent_rationale": classification.rationale,
            "history": context.history,
            "profile": context.profile,
            "current_step": "intent_detected",
        }

    async def execute_tools(self, state: AuraState) -> dict[str, Any]:
        """Run the tools mapped to the detected intent, threading state."""

        intent: Intent = state["intent"]
        tools = self._registry.tools_for(intent)
        merged: dict[str, Any] = dict(state)
        outputs: dict[str, dict[str, Any]] = {}
        executed: list[str] = []

        for tool in tools:
            ctx = ToolRunContext(
                session_id=state["session_id"],
                message=state["message"],
                intent=intent,
                images=state["images"],
                state=merged,
            )
            result = await tool.run(ctx)
            merged.update(result.updates)
            outputs[tool.name] = result.summary()
            if result.status.value == "ok":
                executed.append(tool.name)

        updates: dict[str, Any] = {
            "executed_tools": executed,
            "tool_outputs": outputs,
            "current_step": "tools_executed",
        }
        for key in _DOMAIN_KEYS:
            if merged.get(key) is not None:
                updates[key] = merged[key]

        logger.info(
            "agent.tools_executed",
            intent=intent.value,
            execution_path=list(outputs.keys()),
            tools_succeeded=executed,
        )
        return updates

    async def summarize_node(self, state: AuraState) -> dict[str, Any]:
        """Compose the final reply from the accumulated state."""

        result = await self._summarizer.summarize(state)
        return {
            "final_response": result.text,
            "conversation_summary": result.text[:280],
            "current_step": "summarized",
        }

    async def persist_node(self, state: AuraState) -> dict[str, Any]:
        """Persist the completed turn to memory."""

        ctx = ToolRunContext(
            session_id=state["session_id"],
            message=state["message"],
            intent=state["intent"],
            images=state["images"],
            state=dict(state),
        )
        await self._memory_tool.run(ctx)
        return {"current_step": "persisted"}

    def route_after_intent(self, state: AuraState) -> str:
        """Conditional edge: run tools when the intent maps to any."""

        return "execute_tools" if self._registry.tools_for(state["intent"]) else "summarize"

    # --- Public API -------------------------------------------------------

    async def run(
        self, *, session_id: str, message: str, images: AgentImages | None = None
    ) -> ChatResponse:
        """Execute the full agent graph for one turn."""

        started = perf_counter()
        state = initial_state(session_id, message, images or AgentImages())
        final: AuraState = await self._graph.ainvoke(state)
        latency_ms = round((perf_counter() - started) * 1000, 1)
        logger.info(
            "agent.run",
            session_id=session_id,
            intent=_intent_value(final.get("intent")),
            tools=final.get("executed_tools", []),
            latency_ms=latency_ms,
        )
        return self._to_response(final)

    async def stream(
        self, *, session_id: str, message: str, images: AgentImages | None = None
    ) -> AsyncIterator[AgentStreamEvent]:
        """Run the agent, streaming the final reply token by token."""

        state = initial_state(session_id, message, images or AgentImages())

        state.update(await self.detect_intent(state))  # type: ignore[typeddict-item]
        yield AgentStreamEvent(
            type="intent",
            data={"intent": state["intent"].value, "rationale": state["intent_rationale"]},
        )

        if self._registry.tools_for(state["intent"]):
            state.update(await self.execute_tools(state))  # type: ignore[typeddict-item]
            yield AgentStreamEvent(type="step", data={"tools": state.get("executed_tools", [])})

        buffer: list[str] = []
        async for token in self._summarizer.stream(state):
            buffer.append(token)
            yield AgentStreamEvent(type="token", data={"token": token})

        state["final_response"] = "".join(buffer)
        state["current_step"] = "summarized"
        await self.persist_node(state)
        yield AgentStreamEvent(type="final", data=self._to_response(state).model_dump())

    # --- Helpers ----------------------------------------------------------

    def _to_response(self, state: AuraState) -> ChatResponse:
        outputs = state.get("tool_outputs", {})
        intent_value = _intent_value(state.get("intent"))
        steps = (
            [f"intent:{intent_value}"]
            + [f"{name}:{out['status']}" for name, out in outputs.items()]
            + ["summarized"]
        )
        return ChatResponse(
            session_id=state["session_id"],
            reply=state.get("final_response", ""),
            intent=intent_value,
            tools_used=state.get("executed_tools", []),
            steps=steps,
            recommendations=state.get("recommendations"),
            skin_analysis=state.get("skin_analysis"),
            try_on=state.get("try_on"),
            color_palette=state.get("color_palette"),
        )


def _intent_value(intent: Intent | None) -> str:
    return intent.value if isinstance(intent, Intent) else "UNKNOWN"
