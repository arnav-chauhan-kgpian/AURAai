"""Color analysis service.

Derives a personalised color palette from a user's skin tone / Fitzpatrick type
using established seasonal color theory. This is deterministic reference logic
(no external API), which keeps it fast and easy to reason about and test.
"""

from app.core.logging import get_logger
from app.schemas.color import ColorPalette
from app.schemas.skin import SkinAnalysisResponse

logger = get_logger(__name__)

# Fitzpatrick type -> (undertone, season, recommended, avoid, rationale).
_PALETTES: dict[str, ColorPalette] = {
    "I": ColorPalette(
        fitzpatrick_type="I",
        undertone="cool",
        season="Summer",
        recommended_colors=["soft rose", "powder blue", "lavender", "cool grey", "navy"],
        avoid_colors=["orange", "mustard", "warm brown"],
        rationale="Very fair, cool skin is flattered by soft, muted cool tones.",
    ),
    "II": ColorPalette(
        fitzpatrick_type="II",
        undertone="cool",
        season="Summer",
        recommended_colors=["dusty pink", "periwinkle", "sage", "slate blue", "burgundy"],
        avoid_colors=["neon", "bright orange", "gold"],
        rationale="Fair, cool skin suits gentle, cool-based hues over high-contrast brights.",
    ),
    "III": ColorPalette(
        fitzpatrick_type="III",
        undertone="neutral",
        season="Spring",
        recommended_colors=["teal", "coral", "warm green", "ivory", "denim blue"],
        avoid_colors=["washed-out pastels", "muddy brown"],
        rationale="Neutral medium skin carries both warm and cool clear colors well.",
    ),
    "IV": ColorPalette(
        fitzpatrick_type="IV",
        undertone="warm",
        season="Autumn",
        recommended_colors=["olive", "terracotta", "mustard", "cream", "forest green"],
        avoid_colors=["icy pastel", "cool grey"],
        rationale="Warm olive skin glows in earthy, warm autumnal tones.",
    ),
    "V": ColorPalette(
        fitzpatrick_type="V",
        undertone="warm",
        season="Autumn",
        recommended_colors=["emerald", "cobalt", "ruby", "gold", "rich plum"],
        avoid_colors=["beige", "pale yellow"],
        rationale="Deep warm skin is lifted by saturated jewel tones over pale neutrals.",
    ),
    "VI": ColorPalette(
        fitzpatrick_type="VI",
        undertone="neutral",
        season="Winter",
        recommended_colors=["white", "cobalt", "fuchsia", "emerald", "true red"],
        avoid_colors=["dull brown", "muted khaki"],
        rationale="Rich deep skin pairs strikingly with high-contrast, vivid colors.",
    ),
}

_DEFAULT_TYPE = "IV"


class ColorService:
    """Produces a :class:`ColorPalette` from available skin signals."""

    def derive(
        self,
        *,
        skin_analysis: SkinAnalysisResponse | None = None,
        fitzpatrick_type: str | None = None,
    ) -> ColorPalette:
        """Return a palette for the given Fitzpatrick type or inferred tone."""

        resolved = self._resolve_type(fitzpatrick_type, skin_analysis)
        palette = _PALETTES.get(resolved, _PALETTES[_DEFAULT_TYPE])
        logger.info("color.derived", fitzpatrick_type=resolved, season=palette.season)
        return palette

    def _resolve_type(
        self, fitzpatrick_type: str | None, skin_analysis: SkinAnalysisResponse | None
    ) -> str:
        if fitzpatrick_type:
            key = fitzpatrick_type.strip().upper().replace("TYPE", "").strip()
            if key in _PALETTES:
                return key
        if skin_analysis is not None:
            raw = skin_analysis.raw
            for candidate_key in ("fitzpatrick", "skin_tone", "tone"):
                value = raw.get(candidate_key) if isinstance(raw, dict) else None
                if isinstance(value, str) and value.strip().upper() in _PALETTES:
                    return value.strip().upper()
        return _DEFAULT_TYPE
