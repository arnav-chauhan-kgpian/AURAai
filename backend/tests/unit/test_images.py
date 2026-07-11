"""Unit tests for image utilities."""

from app.utils.images import is_supported_image


def test_supported_image_types_are_accepted() -> None:
    assert is_supported_image("image/png")
    assert is_supported_image("IMAGE/JPEG")


def test_unsupported_image_types_are_rejected() -> None:
    assert not is_supported_image("application/pdf")
