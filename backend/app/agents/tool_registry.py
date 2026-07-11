"""Agent tool registry.

Central catalogue of the agent's capabilities and the intent → tool routing
table. Keeping routing here (not in the graph) means adding a capability is a
data change — register a tool and map it to intents — with no graph edits, which
is the extensibility the design calls for.
"""

from app.core.logging import get_logger
from app.schemas.agent import Intent
from app.tools.base import AuraTool

logger = get_logger(__name__)


class ToolRegistry:
    """Owns the agent's tools and the intent-to-tools routing table."""

    def __init__(self, tools: list[AuraTool]) -> None:
        self._tools: dict[str, AuraTool] = {tool.name: tool for tool in tools}
        self._routes: dict[Intent, list[str]] = {
            Intent.SKIN_ONLY: ["skin_analysis", "recommendation"],
            Intent.TRYON_ONLY: ["virtual_try_on"],
            Intent.STYLE_ONLY: ["color_palette", "recommendation"],
            Intent.SKIN_AND_STYLE: [
                "skin_analysis",
                "color_palette",
                "recommendation",
                "virtual_try_on",
            ],
            Intent.CHAT_ONLY: [],
            Intent.UNKNOWN: [],
        }

    def tools_for(self, intent: Intent) -> list[AuraTool]:
        """Return the ordered tools to run for an intent."""

        names = self._routes.get(intent, [])
        missing = [name for name in names if name not in self._tools]
        if missing:
            logger.warning("registry.missing_tools", intent=intent.value, missing=missing)
        return [self._tools[name] for name in names if name in self._tools]

    def get(self, name: str) -> AuraTool:
        """Return a single tool by its registered name."""

        return self._tools[name]

    def all_tools(self) -> list[AuraTool]:
        return list(self._tools.values())

    def register(self, tool: AuraTool, intents: list[Intent]) -> None:
        """Register a new tool and append it to the given intents' routes.

        Enables extending the agent with new capabilities without touching the
        graph or existing tools.
        """

        self._tools[tool.name] = tool
        for intent in intents:
            self._routes.setdefault(intent, []).append(tool.name)
        logger.info("registry.registered", tool=tool.name, intents=[i.value for i in intents])
