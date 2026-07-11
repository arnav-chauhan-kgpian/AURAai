"""Unit tests for the deterministic color service."""

from app.services.color_service import ColorService


def test_palette_for_fitzpatrick_iv_is_warm_autumn() -> None:
    palette = ColorService().derive(fitzpatrick_type="IV")
    assert palette.season == "Autumn"
    assert palette.undertone == "warm"
    assert "olive" in palette.recommended_colors


def test_palette_normalises_type_label() -> None:
    palette = ColorService().derive(fitzpatrick_type="Type II")
    assert palette.fitzpatrick_type == "II"


def test_palette_defaults_when_unknown() -> None:
    palette = ColorService().derive()
    assert palette.fitzpatrick_type == "IV"
