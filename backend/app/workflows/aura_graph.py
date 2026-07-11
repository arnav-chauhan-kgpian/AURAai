"""AuraAgent LangGraph workflow.

Wires the agent's node methods into a compiled state graph:

    START → detect_intent → (conditional) → execute_tools → summarize
                                     └──────────────────────→ summarize
    summarize → persist_memory → END

Routing is data-driven (the tool registry decides which intents have tools), so
new capabilities extend the agent without changing this graph.
"""

from typing import TYPE_CHECKING

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.state import AuraState

if TYPE_CHECKING:
    from app.agents.agent import AuraAgent


def build_aura_graph(agent: "AuraAgent") -> CompiledStateGraph:
    """Construct and compile the AuraAgent state graph."""

    graph = StateGraph(AuraState)

    graph.add_node("detect_intent", agent.detect_intent)
    graph.add_node("execute_tools", agent.execute_tools)
    graph.add_node("summarize", agent.summarize_node)
    graph.add_node("persist_memory", agent.persist_node)

    graph.set_entry_point("detect_intent")
    graph.add_conditional_edges(
        "detect_intent",
        agent.route_after_intent,
        {"execute_tools": "execute_tools", "summarize": "summarize"},
    )
    graph.add_edge("execute_tools", "summarize")
    graph.add_edge("summarize", "persist_memory")
    graph.add_edge("persist_memory", END)

    return graph.compile()
