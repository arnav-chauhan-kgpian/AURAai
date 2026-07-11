"""Image utilities.

Small, dependency-light helpers for validating and describing image assets. Pure
functions live here so they can be unit tested in isolation.
"""

SUPPORTED_IMAGE_TYPES: frozenset[str] = frozenset(
    {"image/jpeg", "image/png", "image/webp"}
)


def is_supported_image(content_type: str) -> bool:
    """Return whether the given MIME type is an accepted image format."""

    return content_type.lower() in SUPPORTED_IMAGE_TYPES
