"""HistoryService persistence and retrieval, against a fake Supabase client."""

from typing import Any

import pytest

from app.auth.context import RequestContext
from app.schemas.agent import AgentImages
from app.schemas.chat import ChatResponse
from app.schemas.recommendation import RecommendationSet
from app.schemas.skin import OverlayImage, SkinAnalysisResponse, SkinScore
from app.schemas.vto import TryOnResponse
from app.services.history_service import HistoryService


class _Query:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    # Insert path -----------------------------------------------------------
    def insert(self, row: dict[str, Any]) -> "_Query":
        self._pending = row
        return self

    # Select path (all chainable, no-op filters for the test) --------------
    def select(self, *_a: Any, **_k: Any) -> "_Query":
        return self

    def eq(self, *_a: Any, **_k: Any) -> "_Query":
        return self

    def is_(self, *_a: Any, **_k: Any) -> "_Query":
        return self

    def order(self, *_a: Any, **_k: Any) -> "_Query":
        return self

    def limit(self, *_a: Any, **_k: Any) -> "_Query":
        return self

    def execute(self) -> Any:
        if getattr(self, "_pending", None) is not None:
            self._rows.append(self._pending)
            self._pending = None
            return type("R", (), {"data": []})()
        return type("R", (), {"data": list(self._rows)})()


class FakeSupabase:
    def __init__(self) -> None:
        self.tables: dict[str, list[dict[str, Any]]] = {}

    def table(self, name: str) -> _Query:
        return _Query(self.tables.setdefault(name, []))


def _ctx() -> RequestContext:
    return RequestContext(
        user_id="user_1",
        org_id="org_1",
        session_id="sess_1",
        correlation_id="corr_1",
    )


def _full_response() -> ChatResponse:
    return ChatResponse(
        session_id="sess_1",
        reply="Here is your analysis.",
        intent="SKIN_AND_STYLE",
        tools_used=["skin_analysis", "virtual_try_on", "recommendation"],
        skin_analysis=SkinAnalysisResponse(
            task_id="task_skin",
            scores=[SkinScore(concern="acne", raw_score=0.2, ui_score=80.0)],
            overlays=[OverlayImage(concern="acne", url="https://x/overlay.png")],
        ),
        try_on=TryOnResponse(task_id="task_vto", output_images=["https://x/out.png"]),
        recommendations=RecommendationSet(summary="Looks great"),
    )


@pytest.mark.asyncio
async def test_persist_turn_writes_all_tables() -> None:
    db = FakeSupabase()
    service = HistoryService(db, object_store=None)
    images = AgentImages(face_image=b"face", garment_image=b"garment")

    await service.persist_turn(
        _ctx(), message="analyze me", response=_full_response(), images=images
    )

    assert len(db.tables["conversations"]) == 2  # user + assistant
    assert len(db.tables["skin_scans"]) == 1
    assert len(db.tables["try_on_jobs"]) == 1
    assert len(db.tables["recommendations"]) == 1
    scan = db.tables["skin_scans"][0]
    assert scan["task_id"] == "task_skin"
    assert scan["scores"][0]["concern"] == "acne"


@pytest.mark.asyncio
async def test_persist_turn_noop_for_anonymous() -> None:
    db = FakeSupabase()
    service = HistoryService(db, object_store=None)
    ctx = RequestContext(
        user_id="anon",
        org_id="org",
        session_id="s",
        correlation_id="c",
        is_anonymous=True,
    )
    await service.persist_turn(
        ctx, message="hi", response=_full_response(), images=AgentImages()
    )
    assert db.tables == {}


@pytest.mark.asyncio
async def test_fetch_history_returns_persisted_rows() -> None:
    db = FakeSupabase()
    service = HistoryService(db, object_store=None)
    await service.persist_turn(
        _ctx(), message="analyze me", response=_full_response(), images=AgentImages()
    )

    history = await service.fetch_history(_ctx())
    assert len(history["scans"]) == 1
    assert len(history["try_ons"]) == 1
    assert len(history["recommendations"]) == 1


@pytest.mark.asyncio
async def test_disabled_without_supabase() -> None:
    service = HistoryService(None, object_store=None)
    assert service.enabled is False
    await service.persist_turn(
        _ctx(), message="x", response=_full_response(), images=AgentImages()
    )
    assert await service.fetch_history(_ctx()) == {
        "scans": [],
        "try_ons": [],
        "recommendations": [],
    }
