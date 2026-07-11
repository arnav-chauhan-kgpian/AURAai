"""Fakes for agent unit tests: a mock Gemini LLM and mock capability services.

These let the agent, planner, tools, memory and graph be tested end-to-end with
no Gemini or YouCam network calls.
"""

from collections.abc import AsyncIterator

from app.agents.agent import AuraAgent
from app.agents.llm import LLMResult, StructuredResult, TokenUsage
from app.agents.memory import (
    ConversationMemory,
    InMemoryProfileRepository,
    InMemorySessionCache,
)
from app.agents.planner import Planner
from app.agents.summarizer import Summarizer
from app.agents.tool_registry import ToolRegistry
from app.config.config import Settings
from app.schemas.agent import Intent, IntentClassification
from app.schemas.recommendation import ProductRecommendation, RecommendationSet
from app.schemas.skin import OverlayImage, SkinAnalysisResponse, SkinScore
from app.schemas.vto import TryOnResponse
from app.services.color_service import ColorService
from app.tools.color_tool import ColorPaletteTool
from app.tools.memory_tool import ConversationMemoryTool
from app.tools.recommendation_tool import RecommendationTool
from app.tools.skin_tool import SkinAnalysisTool
from app.tools.vto_tool import VirtualTryOnTool


class FakeLLM:
    """A scripted :class:`ChatLLM`: fixed intent, recommendations and summary."""

    model_name = "fake-gemini"

    def __init__(
        self,
        *,
        intent: Intent = Intent.CHAT_ONLY,
        recommendations: RecommendationSet | None = None,
        summary: str = "Here is your personalised advice.",
        raise_on_structured: bool = False,
    ) -> None:
        self._intent = intent
        self._recommendations = recommendations or RecommendationSet(
            summary="A tidy plan.",
            skincare=[ProductRecommendation(title="BHA cleanser", category="skincare", rationale="oil")],
            outfit=[ProductRecommendation(title="olive overshirt", category="outfit", rationale="warm")],
            colors=["olive", "terracotta"],
        )
        self._summary = summary
        self._raise_on_structured = raise_on_structured
        self.calls: list[str] = []

    async def complete(self, *, system: str, prompt: str) -> LLMResult:
        self.calls.append("complete")
        return LLMResult(text=self._summary, usage=TokenUsage(10, 20, 30))

    async def structured(self, *, system: str, prompt: str, schema):
        self.calls.append(f"structured:{schema.__name__}")
        if self._raise_on_structured:
            raise RuntimeError("gemini unavailable")
        if schema is IntentClassification:
            value = IntentClassification(intent=self._intent, rationale="scripted")
        elif schema is RecommendationSet:
            value = self._recommendations
        else:  # pragma: no cover - defensive
            value = schema()
        return StructuredResult(value=value, usage=TokenUsage(5, 5, 10))

    async def stream(self, *, system: str, prompt: str) -> AsyncIterator[str]:
        self.calls.append("stream")
        for token in self._summary.split(" "):
            yield token + " "


class FakeSkinService:
    def __init__(self, response: SkinAnalysisResponse) -> None:
        self._response = response
        self.called = False

    async def analyze(
        self, image, content_type="image/jpeg", file_name="input.jpg", concerns=None
    ) -> SkinAnalysisResponse:
        self.called = True
        return self._response


class FakeVtoService:
    def __init__(self, response: TryOnResponse) -> None:
        self._response = response
        self.called = False

    async def generate_tryon(self, **kwargs) -> TryOnResponse:
        self.called = True
        return self._response


class FakeRecommendationService:
    def __init__(self, response: RecommendationSet) -> None:
        self._response = response
        self.called = False

    async def build(self, context) -> RecommendationSet:
        self.called = True
        return self._response


def sample_skin_response() -> SkinAnalysisResponse:
    return SkinAnalysisResponse(
        task_id="SKIN-TASK",
        scores=[
            SkinScore(concern="acne", raw_score=72.0, ui_score=70.0),
            SkinScore(concern="oiliness", raw_score=60.0, ui_score=58.0),
        ],
        overlays=[OverlayImage(concern="acne", url="https://res/acne.png")],
    )


def sample_tryon_response() -> TryOnResponse:
    return TryOnResponse(task_id="VTO-TASK", output_images=["https://out/render.jpg"])


def make_agent(
    llm: FakeLLM,
    *,
    skin: FakeSkinService | None = None,
    vto: FakeVtoService | None = None,
    recommendation: FakeRecommendationService | None = None,
    memory: ConversationMemory | None = None,
) -> tuple[AuraAgent, dict]:
    """Assemble an AuraAgent with fakes; return the agent and its parts."""

    skin = skin or FakeSkinService(sample_skin_response())
    vto = vto or FakeVtoService(sample_tryon_response())
    recommendation = recommendation or FakeRecommendationService(RecommendationSet(summary="ok"))
    memory = memory or ConversationMemory(
        InMemorySessionCache(), InMemoryProfileRepository(), ttl_seconds=60
    )

    registry = ToolRegistry(
        [
            SkinAnalysisTool(skin),  # type: ignore[arg-type]
            VirtualTryOnTool(vto),  # type: ignore[arg-type]
            ColorPaletteTool(ColorService()),
            RecommendationTool(recommendation),  # type: ignore[arg-type]
        ]
    )
    agent = AuraAgent(
        settings=Settings(),
        planner=Planner(llm),
        registry=registry,
        memory_tool=ConversationMemoryTool(memory),
        summarizer=Summarizer(llm),
    )
    parts = {"skin": skin, "vto": vto, "recommendation": recommendation, "memory": memory}
    return agent, parts
