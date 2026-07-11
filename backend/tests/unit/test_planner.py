"""Unit tests for planner intent routing."""

from app.agents.planner import Planner
from app.schemas.agent import Intent
from tests.unit.fakes import FakeLLM


async def test_planner_uses_llm_classification() -> None:
    planner = Planner(FakeLLM(intent=Intent.SKIN_AND_STYLE))
    result = await planner.classify(
        "I have acne, what should I wear?", has_face_image=True, has_garment_image=True
    )
    assert result.intent is Intent.SKIN_AND_STYLE


async def test_planner_falls_back_to_rules_when_llm_fails() -> None:
    planner = Planner(FakeLLM(raise_on_structured=True))
    result = await planner.classify("My skin feels oily")
    assert result.intent is Intent.SKIN_ONLY


async def test_planner_rule_based_detects_style() -> None:
    planner = Planner(FakeLLM(raise_on_structured=True))
    result = await planner.classify("What colors suit me?")
    assert result.intent is Intent.STYLE_ONLY


async def test_planner_rule_based_tryon_with_garment_image() -> None:
    planner = Planner(FakeLLM(raise_on_structured=True))
    result = await planner.classify("Can I try this?", has_garment_image=True)
    assert result.intent is Intent.TRYON_ONLY
    assert result.wants_tryon is True
