"""YouCam (Perfect Corp) transport client.

The low-level, capability-agnostic client that every YouCam service builds on. It
owns a single pooled ``httpx.AsyncClient`` and centralises the concerns that must
be handled identically for skin analysis and try-on:

* server-to-server authentication with a cached bearer token,
* connection pooling and a bounded concurrency (rate) limiter,
* retry with exponential backoff on transient failures (429/5xx/transport),
* the File API upload handshake,
* task creation and robust status polling with a timeout,
* mapping provider failures onto the application's exception hierarchy,
* structured logging of request id, task id, latency and retry count.
"""

import asyncio
import time
from typing import Any
from uuid import uuid4

import httpx

from app.config.config import Settings
from app.core.exceptions import (
    AuthenticationError,
    ExpiredTaskError,
    InvalidImageError,
    MultipleFacesError,
    NoFaceDetectedError,
    PollingTimeoutError,
    RateLimitError,
    ServerError,
    TaskFailedError,
    YouCamError,
)
from app.core.logging import get_logger
from app.schemas.youcam import (
    ERROR_STATES,
    SUCCESS_STATES,
    FileUploadTarget,
)
from app.utils.crypto import build_id_token

logger = get_logger(__name__)


def classify_youcam_error(
    status_code: int | None,
    error_text: str,
    *,
    default: type[YouCamError] = YouCamError,
    retry_after: float | None = None,
) -> YouCamError:
    """Map an upstream status code and error text onto a typed exception."""

    text = error_text.lower()

    if status_code == 429:
        return RateLimitError(error_text or "Rate limit exceeded", retry_after=retry_after)
    if any(k in text for k in ("no face", "face not found", "face_not", "no_face")):
        return NoFaceDetectedError(error_text or None)
    if any(k in text for k in ("multiple face", "more than one face", "multi_face", "multiface")):
        return MultipleFacesError(error_text or None)
    _invalid = (
        "invalid image", "unsupported", "decode", "bad image", "resolution", "image_error",
        "image_size", "min_image_size", "too small", "too large", "below_min",
    )
    if any(k in text for k in _invalid):
        return InvalidImageError(error_text or None)
    if any(k in text for k in ("expired", "not found", "task_not_found", "no such task")):
        return ExpiredTaskError(error_text or None)
    if status_code is not None and status_code >= 500:
        return ServerError(error_text or None)
    return default(error_text or None)


def _extract_error_text(body: Any) -> str:
    """Pull a human-readable error string out of a decoded response body."""

    if isinstance(body, dict):
        for key in ("error_message", "error", "message", "reason", "status_message"):
            value = body.get(key)
            if isinstance(value, str) and value:
                return value
        result = body.get("result")
        if isinstance(result, dict):
            return _extract_error_text(result)
    if isinstance(body, str):
        return body
    return ""


class YouCamClient:
    """Async transport client for the YouCam server-to-server API."""

    def __init__(self, settings: Settings, http_client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._owns_http = http_client is None
        self._http = http_client or httpx.AsyncClient(
            timeout=httpx.Timeout(
                settings.youcam_request_timeout_seconds,
                connect=settings.youcam_connect_timeout_seconds,
            ),
            limits=httpx.Limits(
                max_connections=settings.youcam_max_connections,
                max_keepalive_connections=settings.youcam_max_keepalive_connections,
            ),
        )
        self._semaphore = asyncio.Semaphore(settings.youcam_max_concurrent_requests)
        self._token: str | None = None
        self._token_expiry: float = 0.0
        self._auth_lock = asyncio.Lock()

    async def aclose(self) -> None:
        """Close the underlying HTTP client if this instance owns it."""

        if self._owns_http:
            await self._http.aclose()

    # --- Authentication ---------------------------------------------------

    async def _token_value(self) -> str:
        """Return a valid bearer token, authenticating (once) if needed."""

        if self._token and time.monotonic() < self._token_expiry:
            return self._token
        async with self._auth_lock:
            if self._token and time.monotonic() < self._token_expiry:
                return self._token
            token = await self._authenticate()
            self._token = token
            self._token_expiry = time.monotonic() + self._settings.youcam_token_ttl_seconds
            return token

    async def _authenticate(self) -> str:
        settings = self._settings
        if not settings.youcam_api_key or not settings.youcam_secret_key:
            raise AuthenticationError("YouCam API key and secret key must be configured")

        id_token = build_id_token(settings.youcam_api_key, settings.youcam_secret_key)
        response = await self._request(
            "POST",
            settings.youcam_auth_url,
            authenticated=False,
            json={"client_id": settings.youcam_api_key, "id_token": id_token},
        )
        body = self._decode(response)
        token = _envelope(body).get("access_token")
        if not isinstance(token, str) or not token:
            raise AuthenticationError("YouCam auth response did not contain an access token")
        return token

    # --- Core request with retry -----------------------------------------

    async def _request(
        self,
        method: str,
        url: str,
        *,
        authenticated: bool = True,
        task_id: str | None = None,
        json: Any = None,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Send a request with retry/backoff, rate limiting and logging."""

        settings = self._settings
        request_id = uuid4().hex
        max_retries = settings.youcam_max_retries
        attempt = 0

        while True:
            attempt += 1
            request_headers = dict(headers or {})
            request_headers.setdefault("X-Request-Id", request_id)
            if authenticated:
                request_headers["Authorization"] = f"Bearer {await self._token_value()}"

            started = time.monotonic()
            try:
                async with self._semaphore:
                    response = await self._http.request(
                        method,
                        url,
                        json=json,
                        content=content,
                        headers=request_headers,
                    )
            except httpx.TransportError as exc:
                latency_ms = round((time.monotonic() - started) * 1000, 1)
                logger.warning(
                    "youcam.request.transport_error",
                    request_id=request_id,
                    task_id=task_id,
                    method=method,
                    url=url,
                    attempt=attempt,
                    latency_ms=latency_ms,
                    error=str(exc),
                )
                if attempt <= max_retries:
                    await asyncio.sleep(self._backoff(attempt))
                    continue
                raise ServerError(f"Transport error contacting YouCam: {exc}") from exc

            latency_ms = round((time.monotonic() - started) * 1000, 1)
            logger.info(
                "youcam.request",
                request_id=request_id,
                task_id=task_id,
                method=method,
                url=url,
                status_code=response.status_code,
                attempt=attempt,
                retry_count=attempt - 1,
                latency_ms=latency_ms,
            )

            if response.status_code in settings.youcam_retry_statuses and attempt <= max_retries:
                delay = self._retry_after(response) or self._backoff(attempt)
                logger.warning(
                    "youcam.request.retry",
                    request_id=request_id,
                    task_id=task_id,
                    status_code=response.status_code,
                    attempt=attempt,
                    retry_in_seconds=round(delay, 3),
                )
                await asyncio.sleep(delay)
                continue

            if response.status_code >= 400:
                self._raise_for_response(response, retry_after=self._retry_after(response))

            return response

    def _backoff(self, attempt: int) -> float:
        """Exponential backoff with full jitter, capped at the configured max."""

        settings = self._settings
        ceiling = min(
            settings.youcam_retry_backoff_max_seconds,
            settings.youcam_retry_backoff_base_seconds * (2 ** (attempt - 1)),
        )
        # Full jitter: uniformly sample within [0, ceiling]. Uses a time-seeded
        # nonce so retries from concurrent callers do not synchronise.
        nonce = (time.monotonic_ns() % 1000) / 1000.0
        return ceiling * nonce

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    def _raise_for_response(self, response: httpx.Response, *, retry_after: float | None) -> None:
        body = self._decode(response, strict=False)
        error_text = _extract_error_text(body) or response.text.strip()
        raise classify_youcam_error(
            response.status_code,
            error_text,
            default=ServerError if response.status_code >= 500 else YouCamError,
            retry_after=retry_after,
        )

    @staticmethod
    def _decode(response: httpx.Response, *, strict: bool = True) -> Any:
        try:
            return response.json()
        except ValueError:
            if strict:
                raise YouCamError("YouCam returned a non-JSON response") from None
            return {"raw": response.text}

    # --- File API ---------------------------------------------------------

    async def request_upload_target(
        self, file_endpoint_url: str, file_name: str, content_type: str, file_size: int
    ) -> FileUploadTarget:
        """Call the File API to obtain a presigned upload target and file id."""

        response = await self._request(
            "POST",
            file_endpoint_url,
            json={
                "files": [
                    {
                        "content_type": content_type,
                        "file_name": file_name,
                        "file_size": file_size,
                    }
                ]
            },
        )
        body = self._decode(response)
        files = _envelope(body).get("files")
        if not isinstance(files, list) or not files:
            raise YouCamError("File API response did not contain an upload target")

        entry = files[0]
        file_id = entry.get("file_id") or entry.get("id")
        requests = entry.get("requests") or []
        if not file_id or not requests:
            raise YouCamError("File API response was missing a file id or upload url")

        upload = requests[0]
        return FileUploadTarget(
            file_id=str(file_id),
            url=upload["url"],
            method=upload.get("method", "PUT"),
            headers={str(k): str(v) for k, v in (upload.get("headers") or {}).items()},
        )

    async def upload_binary(
        self, target: FileUploadTarget, content: bytes, content_type: str
    ) -> None:
        """Upload raw image bytes to a presigned File API target."""

        headers = dict(target.headers)
        headers.setdefault("Content-Type", content_type)
        await self._request(
            target.method,
            target.url,
            authenticated=False,
            content=content,
            headers=headers,
        )

    # --- Tasks ------------------------------------------------------------

    async def create_task(self, task_endpoint_url: str, payload: dict[str, Any]) -> str:
        """Create an AI task and return its ``task_id``."""

        response = await self._request("POST", task_endpoint_url, json=payload)
        body = self._decode(response)
        task_id = _envelope(body).get("task_id")
        if not isinstance(task_id, (str, int)) or task_id == "":
            raise YouCamError("Task creation response did not contain a task id")
        return str(task_id)

    async def get_task(self, task_endpoint_url: str, task_id: str) -> dict[str, Any]:
        """Fetch the current state of a task, returning its ``result`` object."""

        response = await self._request(
            "GET", f"{task_endpoint_url}?task_id={task_id}", task_id=task_id
        )
        return _envelope(self._decode(response))

    async def poll_task(
        self, task_endpoint_url: str, task_id: str, *, path_param: bool = False
    ) -> dict[str, Any]:
        """Poll a task until it reaches a terminal state or the timeout elapses.

        ``path_param=True`` fetches status as ``{url}/{task_id}`` (v2.0 cloth);
        the default uses ``{url}?task_id=`` (v1.0 skin). Status is read from
        ``status`` or ``task_status``.

        Returns the terminal ``result`` object on success; raises
        :class:`PollingTimeoutError` on timeout and a typed error if the task
        finishes in an error state.
        """

        settings = self._settings
        interval = settings.youcam_poll_interval_seconds
        deadline = time.monotonic() + settings.youcam_poll_timeout_seconds
        polls = 0

        status_url = (
            f"{task_endpoint_url}/{task_id}" if path_param
            else f"{task_endpoint_url}?task_id={task_id}"
        )

        while True:
            response = await self._request("GET", status_url, task_id=task_id)
            result = _envelope(self._decode(response))
            status = str(result.get("status") or result.get("task_status") or "").lower()
            polls += 1

            logger.info(
                "youcam.poll",
                task_id=task_id,
                status=status,
                poll_count=polls,
            )

            if status in SUCCESS_STATES:
                return result
            if status in ERROR_STATES:
                error_text = _extract_error_text(result)
                raise classify_youcam_error(None, error_text, default=TaskFailedError)

            if time.monotonic() >= deadline:
                raise PollingTimeoutError(
                    f"Task {task_id} did not complete within "
                    f"{settings.youcam_poll_timeout_seconds:.0f}s ({polls} polls)"
                )
            await asyncio.sleep(interval)

    # --- Result artifacts -------------------------------------------------

    async def download_json(self, url: str) -> Any:
        """Download and decode a JSON result artifact from a (presigned) URL."""

        response = await self._request("GET", url, authenticated=False)
        return self._decode(response)

    async def download_bytes(self, url: str) -> bytes:
        """Download a binary result artifact (e.g. a result ZIP) from a URL."""

        response = await self._request("GET", url, authenticated=False)
        return response.content


def _dig(obj: Any, *keys: str) -> Any:
    """Safely walk nested dict keys, returning ``None`` on any miss."""

    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _envelope(body: Any) -> dict[str, Any]:
    """Return a YouCam response's inner payload.

    YouCam wraps successful payloads in ``result`` (v1.0 endpoints) or ``data``
    (v2.0 endpoints); this normalises both so parsing is wrapper-agnostic.
    """

    if isinstance(body, dict):
        for key in ("result", "data"):
            inner = body.get(key)
            if isinstance(inner, dict):
                return inner
        return body
    return {}
