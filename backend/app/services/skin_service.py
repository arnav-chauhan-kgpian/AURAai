"""Skin analysis service.

Orchestrates the complete YouCam Skin Analysis workflow — upload the image,
create the analysis task, poll until it completes, and parse the result into
domain schemas. Endpoints and agent tools depend on this service rather than
touching the provider directly.
"""

import base64
import io
import json
import zipfile
from typing import Any

from app.config.config import Settings
from app.core.logging import get_logger
from app.schemas.skin import OverlayImage, SkinAnalysisResponse, SkinScore
from app.services.upload_service import UploadService
from app.services.youcam_client import YouCamClient
from app.utils.parsing import IMAGE_EXTENSIONS, collect_urls, url_stem

logger = get_logger(__name__)

# Default set of skin concerns requested from the engine. Overridable per call.
# Valid YouCam HD skin-analysis actions (verified against the live API).
DEFAULT_SKIN_CONCERNS: tuple[str, ...] = (
    "hd_wrinkle",
    "hd_pore",
    "hd_texture",
    "hd_acne",
    "hd_oiliness",
    "hd_moisture",
    "hd_dark_circle",
    "hd_eye_bag",
    "hd_radiance",
    "hd_redness",
    "hd_age_spot",
    "hd_firmness",
    "hd_droopy_upper_eyelid",
    "hd_droopy_lower_eyelid",
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
                "actions": [{"id": 0, "dst_actions": actions}],
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
        scores: list[SkinScore] = []
        overlays: list[OverlayImage] = []

        # Live YouCam delivers the result as a ZIP containing `score_info.json`
        # plus per-concern mask PNGs.
        zip_urls = [u for u in urls if ".zip" in u.lower()]
        if zip_urls:
            try:
                blob = await self._client.download_bytes(zip_urls[0])
                scores, overlays = _parse_skin_zip(blob)
            except Exception:  # noqa: BLE001 - a bad artifact must not fail the whole run
                logger.warning("skin.result.zip_parse_failed", task_id=task_id)
        else:
            # Fallback: loose JSON/image artifacts (older/alternate shapes).
            for url in (u for u in urls if ".json" in u.lower()):
                try:
                    scores.extend(_parse_scores(await self._client.download_json(url)))
                except Exception:  # noqa: BLE001
                    logger.warning("skin.result.score_download_failed", task_id=task_id, url=url)
            overlays = [
                OverlayImage(concern=url_stem(u), url=u)
                for u in urls
                if any(ext in u.lower() for ext in IMAGE_EXTENSIONS)
            ]

        logger.info(
            "skin.result.parsed",
            task_id=task_id,
            score_count=len(scores),
            overlay_count=len(overlays),
        )
        return SkinAnalysisResponse(
            task_id=task_id, scores=scores, overlays=overlays, raw=result
        )


# Skip embedding any single mask larger than this (keeps the response bounded);
# YouCam concern masks are small grayscale PNGs well under this ceiling.
_MAX_MASK_BYTES = 500_000
_MASK_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def _parse_skin_zip(blob: bytes) -> tuple[list[SkinScore], list[OverlayImage]]:
    """Parse a YouCam skin-analysis result ZIP into scores and heatmap overlays.

    The archive holds ``score_info.json`` mapping each ``hd_<concern>`` to
    ``{raw_score, ui_score, output_mask_name}`` plus the per-concern mask images.
    Scores are parsed directly; each mask image is embedded as a ``data:`` URI so
    the client can render a real heatmap without a second network round-trip. The
    ``hd_`` prefix is stripped for display.
    """

    scores: list[SkinScore] = []
    overlays: list[OverlayImage] = []

    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        names = archive.namelist()
        info_name = next(
            (n for n in names if n.lower().endswith("score_info.json")), None
        )
        if not info_name:
            return scores, overlays
        info = json.loads(archive.read(info_name))
        masks_by_base = {n.rsplit("/", 1)[-1]: n for n in names if n.lower().endswith(_MASK_EXTS)}

        if not isinstance(info, dict):
            return scores, overlays

        for concern, value in info.items():
            if not isinstance(value, dict):
                continue
            raw = _coerce_float(value.get("raw_score"))
            ui = _coerce_float(value.get("ui_score"))
            label = concern[3:] if concern.startswith("hd_") else concern
            if raw is not None or ui is not None:
                scores.append(
                    SkinScore(
                        concern=label, raw_score=raw or ui or 0.0, ui_score=ui or raw or 0.0
                    )
                )
            overlay = _mask_overlay(archive, masks_by_base, label, value)
            if overlay is not None:
                overlays.append(overlay)

    return scores, overlays


def _mask_overlay(
    archive: zipfile.ZipFile,
    masks_by_base: dict[str, str],
    label: str,
    value: dict[str, Any],
) -> OverlayImage | None:
    """Embed a concern's mask image (if any) as a data-URI overlay."""

    mask_name = value.get("output_mask_name") or value.get("mask_name")
    entry: str | None = None
    if mask_name:
        entry = masks_by_base.get(str(mask_name).rsplit("/", 1)[-1])
    if entry is None:
        # Fallback: match a mask file whose name contains the concern label.
        entry = next((n for base, n in masks_by_base.items() if label in base.lower()), None)
    if entry is None:
        return None

    data = archive.read(entry)
    if not data or len(data) > _MAX_MASK_BYTES:
        return None
    mime = "image/jpeg" if entry.lower().endswith((".jpg", ".jpeg")) else "image/png"
    encoded = base64.b64encode(data).decode("ascii")
    return OverlayImage(concern=label, url=f"data:{mime};base64,{encoded}")


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
