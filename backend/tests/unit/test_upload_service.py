"""Unit tests for the upload service (YouCam File API)."""

import httpx

from app.services.upload_service import UploadService


async def test_upload_returns_file_id(youcam) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/file/skin-analysis") and request.method == "POST":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "files": [
                            {
                                "file_id": "FILE-9",
                                "requests": [
                                    {"url": "https://up.example/o", "method": "PUT", "headers": {}}
                                ],
                            }
                        ]
                    }
                },
            )
        if request.url.host == "up.example" and request.method == "PUT":
            return httpx.Response(200)
        return httpx.Response(404, json={"error": "unexpected"})

    client, settings = youcam(handler)
    service = UploadService(settings, client)

    result = await service.upload(
        settings.youcam_file_skin_url, b"abc", "image/jpeg", "photo.jpg"
    )
    assert result.file_id == "FILE-9"
    assert result.size_bytes == 3
    assert result.content_type == "image/jpeg"
