"""Unit tests for the YouCam transport client."""

import httpx
import pytest

from app.core.exceptions import (
    AuthenticationError,
    InvalidImageError,
    NoFaceDetectedError,
    PollingTimeoutError,
    RateLimitError,
)


async def test_request_upload_target_and_upload_binary(youcam) -> None:
    puts: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/file/skin-analysis") and request.method == "POST":
            return httpx.Response(
                200,
                json={
                    "result": {
                        "files": [
                            {
                                "file_id": "FILE-1",
                                "requests": [
                                    {
                                        "url": "https://upload.example/put/FILE-1",
                                        "method": "PUT",
                                        "headers": {"Content-Type": "image/jpeg"},
                                    }
                                ],
                            }
                        ]
                    }
                },
            )
        if request.url.host == "upload.example" and request.method == "PUT":
            puts.append(request.content)
            return httpx.Response(200)
        return httpx.Response(404, json={"error": "unexpected"})

    client, settings = youcam(handler)

    target = await client.request_upload_target(
        settings.youcam_file_skin_url, "photo.jpg", "image/jpeg", 2048
    )
    assert target.file_id == "FILE-1"
    assert target.method == "PUT"

    await client.upload_binary(target, b"binary-image-bytes", "image/jpeg")
    assert puts == [b"binary-image-bytes"]


async def test_poll_task_succeeds_after_running(youcam) -> None:
    state = {"calls": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        state["calls"] += 1
        status = "running" if state["calls"] < 3 else "success"
        return httpx.Response(200, json={"result": {"status": status, "task_id": "T1"}})

    client, settings = youcam(handler)

    result = await client.poll_task(settings.youcam_task_skin_url, "T1")
    assert result["status"] == "success"
    assert state["calls"] == 3


async def test_poll_task_times_out(youcam) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"result": {"status": "running"}})

    client, settings = youcam(
        handler, youcam_poll_timeout_seconds=0.15, youcam_poll_interval_seconds=0.03
    )

    with pytest.raises(PollingTimeoutError):
        await client.poll_task(settings.youcam_task_skin_url, "T1")


async def test_retries_on_429_then_succeeds(youcam) -> None:
    state = {"calls": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        state["calls"] += 1
        if state["calls"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"error": "slow down"})
        return httpx.Response(200, json={"result": {"task_id": "T-OK"}})

    client, settings = youcam(handler)

    task_id = await client.create_task(settings.youcam_task_skin_url, {"payload": {}})
    assert task_id == "T-OK"
    assert state["calls"] == 2


async def test_rate_limit_raised_after_retries_exhausted(youcam) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "too many requests"})

    client, settings = youcam(handler, youcam_max_retries=2)

    with pytest.raises(RateLimitError):
        await client.create_task(settings.youcam_task_skin_url, {})


async def test_invalid_image_http_error_mapped(youcam) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "Invalid image format"})

    client, settings = youcam(handler)

    with pytest.raises(InvalidImageError):
        await client.create_task(settings.youcam_task_skin_url, {})


async def test_task_error_status_mapped_to_no_face(youcam) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"result": {"status": "error", "error": "No face detected in image"}}
        )

    client, settings = youcam(handler)

    with pytest.raises(NoFaceDetectedError):
        await client.poll_task(settings.youcam_task_skin_url, "T1")


async def test_missing_credentials_raise_authentication_error(youcam) -> None:
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover - never reached
        return httpx.Response(200, json={})

    client, settings = youcam(
        handler, preseed=False, youcam_api_key="", youcam_secret_key=""
    )

    with pytest.raises(AuthenticationError):
        await client.create_task(settings.youcam_task_skin_url, {})
