"""End-to-end tests for the AuraAgent LangGraph workflow."""

from app.schemas.agent import AgentImages, Intent
from tests.unit.fakes import FakeLLM, make_agent


async def test_skin_and_style_runs_full_pipeline() -> None:
    llm = FakeLLM(
        intent=Intent.SKIN_AND_STYLE,
        summary="Your acne is elevated, so olive and terracotta suit you. Here is the jacket on you.",
    )
    agent, parts = make_agent(llm)
    images = AgentImages(face_image=b"face-bytes", garment_image=b"jacket-bytes")

    response = await agent.run(
        session_id="sess-1",
        message="I have acne, what should I wear? Can I try this jacket?",
        images=images,
    )

    # The graph selected Skin Analysis → Color → Recommendation → Try-On.
    assert response.intent == "SKIN_AND_STYLE"
    assert response.tools_used == [
        "skin_analysis",
        "color_palette",
        "recommendation",
        "virtual_try_on",
    ]
    assert response.skin_analysis is not None and response.skin_analysis.task_id == "SKIN-TASK"
    assert response.try_on is not None and response.try_on.task_id == "VTO-TASK"
    assert response.color_palette is not None
    assert response.recommendations is not None
    assert "olive" in response.reply
    # Execution path is reflected in steps.
    assert response.steps[0] == "intent:SKIN_AND_STYLE"
    assert response.steps[-1] == "summarized"


async def test_run_persists_turn_to_memory() -> None:
    agent, parts = make_agent(FakeLLM(intent=Intent.SKIN_ONLY))

    await agent.run(
        session_id="mem-sess",
        message="Analyze my skin",
        images=AgentImages(face_image=b"x"),
    )

    context = await parts["memory"].recall("mem-sess")
    assert len(context.history) == 2  # user + assistant
    assert context.snapshot.get("skin_analysis") is not None
    assert context.profile.get("skin_type") == "acne"


async def test_chat_only_skips_tools() -> None:
    agent, _ = make_agent(FakeLLM(intent=Intent.CHAT_ONLY, summary="Hi there, how can I help?"))

    response = await agent.run(session_id="s", message="hello")

    assert response.tools_used == []
    assert response.reply.startswith("Hi there")


async def test_stream_emits_intent_tokens_and_final() -> None:
    agent, parts = make_agent(FakeLLM(intent=Intent.SKIN_ONLY, summary="one two three"))

    events = [
        event
        async for event in agent.stream(
            session_id="stream-sess",
            message="Analyze my skin",
            images=AgentImages(face_image=b"x"),
        )
    ]
    types = [event.type for event in events]

    assert types[0] == "intent"
    assert "step" in types
    assert "token" in types
    assert types[-1] == "final"

    streamed = "".join(e.data["token"] for e in events if e.type == "token")
    assert "one" in streamed and "three" in streamed

    context = await parts["memory"].recall("stream-sess")
    assert len(context.history) == 2
