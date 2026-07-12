"""End-to-end unit test for the virtual try-on workflow (mocked YouCam)."""

import httpx

from app.services.upload_service import UploadService
from app.services.vto_service import VirtualTryOnService


def _cloth_handler(request: httpx.Request) -> httpx.Response:
    path, method, host = request.url.path, request.method, request.url.host

    if path.endswith("/file/cloth") and method == "POST":
        return httpx.Response(
            200,
            json={
                "result": {
                    "files": [
                        {
                            "file_id": "CLOTH-FILE",
                            "requests": [
                                {"url": "https://up.example/o", "method": "PUT", "headers": {}}
                            ],
                        }
                    ]
                }
            },
        )
    if host == "up.example" and method == "PUT":
        return httpx.Response(200)
    # v2.0 cloth: flat POST payload; status fetched by path param with `data`
    # wrapper + `task_status` field + `results.url` (verified against live API).
    if path.endswith("/task/cloth") and method == "POST":
        return httpx.Response(200, json={"data": {"task_id": "VTO-TASK"}})
    if "/task/cloth/" in path and method == "GET":
        return httpx.Response(
            200,
            json={
                "data": {
                    "task_status": "success",
                    "error": None,
                    "results": {"url": "https://out.example/render.jpg"},
                }
            },
        )
    return httpx.Response(404, json={"error": "unexpected path"})


async def test_generate_tryon_runs_full_workflow(youcam) -> None:
    client, settings = youcam(_cloth_handler)
    service = VirtualTryOnService(settings, client, UploadService(settings, client))

    result = await service.generate_tryon(
        user_image=b"person-bytes",
        clothing_image=b"garment-bytes",
        garment_category="upper_body",
    )

    assert result.task_id == "VTO-TASK"
    assert result.output_images == ["https://out.example/render.jpg"]
