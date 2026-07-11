"""Parsing helpers for provider result payloads."""

from typing import Any

IMAGE_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".webp")


def collect_urls(obj: Any) -> list[str]:
    """Recursively collect string values stored under a ``url`` key."""

    found: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "url" and isinstance(value, str):
                    found.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(obj)
    return found


def url_stem(url: str) -> str:
    """Return the file stem of a URL (no query string, no extension)."""

    tail = url.split("?", 1)[0].rstrip("/").rsplit("/", 1)[-1]
    return tail.rsplit(".", 1)[0] or "overlay"
