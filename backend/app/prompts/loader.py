"""Prompt template loader.

Prompt text lives in Markdown files alongside this module so it is versionable
and reviewable independently of code. Templates are read once and cached.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent


class Prompt(str, Enum):
    """Available prompt templates (file stems in this directory)."""

    SYSTEM = "system"
    PLANNER = "planner"
    STYLIST = "stylist"
    SKIN = "skin"
    FASHION = "fashion"


@lru_cache
def load_prompt(prompt: Prompt) -> str:
    """Return the text of a prompt template, cached after first read."""

    path = _PROMPTS_DIR / f"{prompt.value}.md"
    return path.read_text(encoding="utf-8").strip()
