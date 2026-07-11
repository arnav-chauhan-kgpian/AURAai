"""End-to-end unit test for the skin analysis workflow (mocked YouCam)."""

import httpx

from app.services.skin_service import SkinService
from app.services.upload_service import UploadService


def _skin_handler(request: httpx.Request) -> httpx.Response:
    path, method, host = request.url.path, request.method, request.url.host

    if path.endswith("/file/skin-analysis") and method == "POST":
        return httpx.Response(
            200,
            json={
                "result": {
                    "files": [
                        {
                            "file_id": "SRC-1",
                            "requests": [
                                {"url": "https://up.example/src", "method": "PUT", "headers": {}}
                            ],
                        }
                    ]
                }
            },
        )
    if host == "up.example" and method == "PUT":
        return httpx.Response(200)
    if path.endswith("/task/skin-analysis") and method == "POST":
        return httpx.Response(200, json={"result": {"task_id": "SKIN-TASK"}})
    if path.endswith("/task/skin-analysis") and method == "GET":
        return httpx.Response(
            200,
            json={
                "result": {
                    "status": "success",
                    "results": [
                        {
                            "data": [
                                {"url": "https://res.example/scores.json"},
                                {"url": "https://res.example/mask_pore.png"},
                            ]
                        }
                    ],
                }
            },
        )
    if host == "res.example" and path.endswith("scores.json"):
        return httpx.Response(
            200,
            json={
                "pore": {"raw_score": 70, "ui_score": 65},
                "wrinkle": {"raw_score": 40, "ui_score": 42},
            },
        )
    return httpx.Response(404, json={"error": "unexpected path"})


async def test_analyze_runs_full_workflow(youcam) -> None:
    client, settings = youcam(_skin_handler)
    service = SkinService(settings, client, UploadService(settings, client))

    result = await service.analyze(b"image-bytes", content_type="image/jpeg")

    assert result.task_id == "SKIN-TASK"
    concerns = {s.concern for s in result.scores}
    assert concerns == {"pore", "wrinkle"}
    pore = next(s for s in result.scores if s.concern == "pore")
    assert pore.raw_score == 70.0
    assert pore.ui_score == 65.0
    assert len(result.overlays) == 1
    assert result.overlays[0].url.endswith("mask_pore.png")
