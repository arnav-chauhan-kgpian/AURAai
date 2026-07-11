"""Upload validation and virus-scan hook.

Defends the image ingest path: enforces a max size, an allow-list of MIME types,
and — critically — verifies the **magic bytes** so a caller can't smuggle a
non-image (or a mislabelled file) past a spoofed ``Content-Type``. An optional
ClamAV hook scans bytes before they are ever processed or stored.
"""

from app.config.config import Settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Leading signatures for the formats we accept.
_MAGIC = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],  # RIFF....WEBP — WEBP checked separately below
}


def _matches_magic(content_type: str, data: bytes) -> bool:
    if content_type == "image/webp":
        return data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return any(data.startswith(sig) for sig in _MAGIC.get(content_type, []))


def validate_image_upload(
    settings: Settings, *, content: bytes, content_type: str | None, filename: str | None
) -> str:
    """Validate an uploaded image; return the confirmed content type.

    Raises :class:`ValidationError` on any violation.
    """

    if not content:
        raise ValidationError("Empty upload")

    if len(content) > settings.max_upload_bytes:
        raise ValidationError(
            f"File exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB limit"
        )

    ctype = (content_type or "").split(";")[0].strip().lower()
    if ctype not in settings.allowed_image_types:
        raise ValidationError(f"Unsupported image type: {ctype or 'unknown'}")

    if not _matches_magic(ctype, content):
        logger.warning("upload.magic_mismatch", filename=filename, content_type=ctype)
        raise ValidationError("File contents do not match a supported image format")

    return ctype


async def scan_for_viruses(settings: Settings, content: bytes) -> None:
    """Optional ClamAV scan hook. No-op unless ``virus_scan_enabled``.

    Fails **closed** — if scanning is required but the scanner is unreachable, the
    upload is rejected rather than trusted.
    """

    if not settings.virus_scan_enabled:
        return
    try:
        import clamd  # type: ignore[import-not-found]  # optional dependency

        client = clamd.ClamdNetworkSocket(host=settings.clamav_host, port=settings.clamav_port)
        result = client.instream(_to_buffer(content))
        status = result.get("stream", ("OK", None))[0] if isinstance(result, dict) else "ERROR"
        if status != "OK":
            raise ValidationError("Upload failed virus scan")
    except ValidationError:
        raise
    except Exception as exc:  # noqa: BLE001 - fail closed when scanning is required
        logger.error("upload.virus_scan_failed", error=str(exc))
        raise ValidationError("Virus scanning is unavailable") from exc


def _to_buffer(content: bytes):
    from io import BytesIO

    return BytesIO(content)
