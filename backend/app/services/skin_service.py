"""Skin analysis service.

Orchestrates the complete YouCam Skin Analysis workflow — upload the image,
create the analysis task, poll until it completes, and parse the result into
domain schemas. Endpoints and agent tools depend on this service rather than
touching the provider directly.
"""

from typing import Any

from app.config.config import Settings
from app.core.logging import get_logger
from app.schemas.skin import OverlayImage, SkinAnalysisResponse, SkinScore
from app.services.upload_service import UploadService
from app.services.youcam_client import YouCamClient
from app.utils.parsing import IMAGE_EXTENSIONS, collect_urls, url_stem

logger = get_logger(__name__)

# Default set of skin concerns requested from the engine. Overridable per call.
DEFAULT_SKIN_CONCERNS: tuple[str, ...] = (
    "wrinkle",
    "pore",
    "spot",
    "texture",
    "acne",
    "dark_circle",
    "eye_bag",
    "radiance",
    "oiliness",
    "moisture",
    "redness",
    "firmness",
    "age_spot",
    "droopy_eyelid",
)


class SkinService:
    """Coordinates facial skin analysis via the YouCam Skin Analysis API."""

    def __init__(
        self, settings: Settings, client: YouCamClient, upload_service: UploadService
    ) -> None:
        self._settings = settings
        self._client = client
        self._uploads = upload_service

    async def upload_image(
        self, content: bytes, content_type: str = "image/jpeg", file_name: str = "input.jpg"
    ) -> str:
        """Upload the source image and return its ``file_id``."""

        result = await self._uploads.upload(
            self._settings.youcam_file_skin_url, content, content_type, file_name
        )
        return result.file_id

    async def create_skin_analysis_task(
        self, file_id: str, concerns: list[str] | None = None
    ) -> str:
        """Create a skin analysis task for an uploaded image and return its id."""

        actions = list(concerns) if concerns else list(DEFAULT_SKIN_CONCERNS)
        payload = {
            "request_id": 0,
            "payload": {
                "file_sets": {"src_ids": [file_id]},
                "dst_actions": actions,
            },
        }
        return await self._client.create_task(self._settings.youcam_task_skin_url, payload)

    async def poll_skin_analysis(self, task_id: str) -> dict[str, Any]:
        """Poll a skin analysis task until it reaches a terminal state."""

        return await self._client.poll_task(self._settings.youcam_task_skin_url, task_id)

    async def analyze(
        self,
        image: bytes,
        content_type: str = "image/jpeg",
        file_name: str = "input.jpg",
        concerns: list[str] | None = None,
    ) -> SkinAnalysisResponse:
        """Run the end-to-end skin analysis workflow and return parsed scores."""

        file_id = await self.upload_image(image, content_type, file_name)
        task_id = await self.create_skin_analysis_task(file_id, concerns)
        logger.info("skin.task.created", task_id=task_id, file_id=file_id)

        result = await self.poll_skin_analysis(task_id)
        return await self._parse_result(task_id, result)

    async def _parse_result(self, task_id: str, result: dict[str, Any]) -> SkinAnalysisResponse:
        """Parse a successful poll result into scores and overlay images.

        Skin analysis emits result artifacts as URLs: a JSON scores document and
        per-concern mask images. Score documents are downloaded and parsed; image
        URLs become overlays. The full result is retained in ``raw``.
        """

        urls = collect_urls(result)
        score_urls = [u for u in urls if ".json" in u.lower()]
        image_urls = [u for u in urls if any(ext in u.lower() for ext in IMAGE_EXTENSIONS)]

        scores: list[SkinScore] = []
        for url in score_urls:
            try:
                document = await self._client.download_json(url)
            except Exception:  # noqa: BLE001 - a bad artifact must not fail the whole run
                logger.warning("skin.result.score_download_failed", task_id=task_id, url=url)
                continue
            scores.extend(_parse_scores(document))

        overlays = [OverlayImage(concern=url_stem(u), url=u) for u in image_urls]

        logger.info(
            "skin.result.parsed",
            task_id=task_id,
            score_count=len(scores),
            overlay_count=len(overlays),
        )
        return SkinAnalysisResponse(
            task_id=task_id, scores=scores, overlays=overlays, raw=result
        )


def _parse_scores(document: Any) -> list[SkinScore]:
    """Parse a skin scores document (dict-of-concern or list) into SkinScores."""

    scores: list[SkinScore] = []

    if isinstance(document, dict):
        # Prefer a nested "scores"/"result" section when present.
        for container_key in ("scores", "result", "data"):
            nested = document.get(container_key)
            if isinstance(nested, (dict, list)):
                return _parse_scores(nested)
        for concern, value in document.items():
            score = _score_from(concern, value)
            if score is not None:
                scores.append(score)
    elif isinstance(document, list):
        for item in document:
            if isinstance(item, dict):
                concern = str(
                    item.get("name") or item.get("concern") or item.get("type") or "unknown"
                )
                score = _score_from(concern, item)
                if score is not None:
                    scores.append(score)

    return scores


def _score_from(concern: str, value: Any) -> SkinScore | None:
    if isinstance(value, dict):
        raw = _coerce_float(value.get("raw_score", value.get("raw", value.get("score"))))
        ui = _coerce_float(value.get("ui_score", value.get("ui", value.get("score"))))
    elif isinstance(value, (int, float)):
        raw = ui = float(value)
    else:
        return None
    if raw is None and ui is None:
        return None
    return SkinScore(concern=concern, raw_score=raw or ui or 0.0, ui_score=ui or raw or 0.0)


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None
