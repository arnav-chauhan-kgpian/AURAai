"""Guards against the LLM inventing a tried-on garment's color.

The system never sees the garment during a virtual try-on, so both the reply
context and the recommendation prompt must instruct the model not to name or
guess the garment's color/pattern/material.
"""

from app.schemas.recommendation import RecommendationContext
from app.schemas.vto import TryOnResponse
from app.services.recommendation_service import RecommendationService


def test_recommendation_prompt_has_garment_color_guardrail_when_try_on() -> None:
    ctx = RecommendationContext(
        message="how does this look?",
        intent="TRY_ON",
        try_on_images=["https://x/out.png"],
    )
    prompt = RecommendationService._render_prompt(ctx)
    lowered = prompt.lower()
    assert "cannot see the garment" in lowered
    assert "color" in lowered


def test_recommendation_prompt_omits_guardrail_without_try_on() -> None:
    ctx = RecommendationContext(message="skincare help", intent="SKIN")
    prompt = RecommendationService._render_prompt(ctx)
    assert "cannot see the garment" not in prompt.lower()


def test_summarizer_context_warns_not_to_name_garment_color() -> None:
    from app.agents.summarizer import _compact_context

    state = {
        "message": "how does the dress look?",
        "intent": "TRY_ON",
        "try_on": TryOnResponse(task_id="t", output_images=["https://x/out.png"]),
    }
    context = _compact_context(state)  # type: ignore[arg-type]
    lowered = context.lower()
    assert "cannot see the garment" in lowered
    assert "never name or guess its color" in lowered
