"""Input sanitization for free-text fields.

Strips control characters, normalises whitespace, and bounds length. Applied to
the chat message before it reaches the agent — defensive hygiene, not a
replacement for the model's own prompt handling.
"""

import re
import unicodedata

from app.core.exceptions import ValidationError

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MAX_MESSAGE_CHARS = 4000


def sanitize_text(value: str, *, max_length: int = _MAX_MESSAGE_CHARS, field: str = "input") -> str:
    """Return a cleaned string or raise :class:`ValidationError`."""

    if not isinstance(value, str):
        raise ValidationError(f"{field} must be text")

    normalized = unicodedata.normalize("NFC", value)
    cleaned = _CONTROL.sub("", normalized).strip()

    if not cleaned:
        raise ValidationError(f"{field} must not be empty")
    if len(cleaned) > max_length:
        raise ValidationError(f"{field} exceeds {max_length} characters")

    return cleaned
