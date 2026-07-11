"""Unit tests for conversation memory."""

from app.agents.memory import (
    ConversationMemory,
    InMemoryProfileRepository,
    InMemorySessionCache,
)
from app.schemas.chat import ChatMessage
from tests.unit.fakes import sample_skin_response


def _memory() -> ConversationMemory:
    return ConversationMemory(
        InMemorySessionCache(), InMemoryProfileRepository(), ttl_seconds=60
    )


async def test_persist_and_recall_roundtrip() -> None:
    memory = _memory()
    await memory.persist(
        "s1",
        user_message=ChatMessage(role="user", content="analyze my skin"),
        assistant_message=ChatMessage(role="assistant", content="Done — here are your scores."),
        skin_analysis=sample_skin_response(),
        profile_updates={"skin_type": "acne", "fitzpatrick_type": "IV"},
    )

    context = await memory.recall("s1")
    assert [m.content for m in context.history] == [
        "analyze my skin",
        "Done — here are your scores.",
    ]
    assert context.profile["skin_type"] == "acne"
    assert context.snapshot["skin_analysis"]["task_id"] == "SKIN-TASK"


async def test_conversation_replay_preserves_order() -> None:
    memory = _memory()
    for content, role in [("one", "user"), ("two", "assistant"), ("three", "user")]:
        await memory.append_message("s2", ChatMessage(role=role, content=content))  # type: ignore[arg-type]

    context = await memory.recall("s2")
    assert [m.content for m in context.history] == ["one", "two", "three"]
