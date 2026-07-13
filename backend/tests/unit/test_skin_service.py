"""End-to-end unit test for the skin analysis workflow (mocked YouCam)."""

import io
import json
import zipfile

import httpx

from app.services.skin_service import SkinService, _parse_skin_zip
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


# A 1x1 PNG (smallest valid image) used as a fake concern mask.
_PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c6360000002000155a2b4ee0000000049454e44ae426082"
)


def test_parse_skin_zip_extracts_scores_and_mask_overlays() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "score_info.json",
            json.dumps(
                {
                    "hd_acne": {"raw_score": 20, "ui_score": 80, "output_mask_name": "acne.png"},
                    "hd_pore": {"raw_score": 30, "ui_score": 70, "output_mask_name": "pore.png"},
                }
            ),
        )
        archive.writestr("acne.png", _PNG_1PX)
        archive.writestr("pore.png", _PNG_1PX)

    scores, overlays = _parse_skin_zip(buffer.getvalue())

    assert {s.concern for s in scores} == {"acne", "pore"}
    assert len(overlays) == 2
    assert all(o.url.startswith("data:image/png;base64,") for o in overlays)
    assert {o.concern for o in overlays} == {"acne", "pore"}
