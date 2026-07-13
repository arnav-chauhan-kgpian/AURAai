"""Tolerant parsing of list-typed settings from env vars.

A platform env var like CORS_ORIGINS is frequently set as a bare URL or a
comma-separated string rather than strict JSON. These must not crash startup.
"""

import pytest

from app.config.config import Settings, _parse_str_list


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('["https://a.app","https://b.app"]', ["https://a.app", "https://b.app"]),
        ("https://a.app", ["https://a.app"]),
        ("https://a.app,https://b.app", ["https://a.app", "https://b.app"]),
        ("https://a.app, https://b.app", ["https://a.app", "https://b.app"]),
        ("", []),
        ("https://a.app,", ["https://a.app"]),
        ("[bad json", ["[bad json"]),  # falls back to non-JSON handling
    ],
)
def test_parse_str_list(raw: str, expected: list[str]) -> None:
    assert _parse_str_list(raw) == expected


def test_settings_accept_bare_url_for_list_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://app.up.railway.app")
    monkeypatch.setenv("CLERK_AUTHORIZED_PARTIES", "https://app.up.railway.app")
    settings = Settings()
    assert settings.cors_origins == ["https://app.up.railway.app"]
    assert settings.clerk_authorized_parties == ["https://app.up.railway.app"]


def test_settings_accept_json_array(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["https://a.app","https://b.app"]')
    settings = Settings()
    assert settings.cors_origins == ["https://a.app", "https://b.app"]
