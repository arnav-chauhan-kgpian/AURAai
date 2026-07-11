"""Unit tests for intent → tool routing and execution."""

from app.schemas.agent import AgentImages, Intent
from tests.unit.fakes import FakeLLM, make_agent


def test_registry_routes_each_intent() -> None:
    agent, _ = make_agent(FakeLLM())
    registry = agent._registry  # noqa: SLF001 - inspecting routing in a unit test

    def names(intent: Intent) -> list[str]:
        return [tool.name for tool in registry.tools_for(intent)]

    assert names(Intent.SKIN_ONLY) == ["skin_analysis", "recommendation"]
    assert names(Intent.TRYON_ONLY) == ["virtual_try_on"]
    assert names(Intent.STYLE_ONLY) == ["color_palette", "recommendation"]
    assert names(Intent.SKIN_AND_STYLE) == [
        "skin_analysis",
        "color_palette",
        "recommendation",
        "virtual_try_on",
    ]
    assert names(Intent.CHAT_ONLY) == []


async def test_style_only_does_not_invoke_skin_analysis() -> None:
    agent, parts = make_agent(FakeLLM(intent=Intent.STYLE_ONLY))

    response = await agent.run(session_id="s", message="What colors suit me?")

    assert parts["skin"].called is False
    assert response.tools_used == ["color_palette", "recommendation"]
    assert response.color_palette is not None


async def test_tryon_only_invokes_only_try_on() -> None:
    agent, parts = make_agent(FakeLLM(intent=Intent.TRYON_ONLY))
    images = AgentImages(face_image=b"person", garment_image=b"jacket")

    response = await agent.run(session_id="s", message="Can I try this jacket?", images=images)

    assert parts["vto"].called is True
    assert parts["skin"].called is False
    assert response.tools_used == ["virtual_try_on"]
