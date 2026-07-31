"""Language detection.

A Cyrillic-share heuristic, deliberately: it is dependency-free, has no cold
start, and is right for the RU/EN split this product ships with. Users can
always override with /lang, and the choice is persisted per user.
"""

from __future__ import annotations

from .models import Lang

CYRILLIC_RANGES = ((0x0400, 0x04FF), (0x0500, 0x052F))


def _is_cyrillic(char: str) -> bool:
    point = ord(char)
    return any(lo <= point <= hi for lo, hi in CYRILLIC_RANGES)


def detect(text: str, default: Lang = Lang.EN) -> Lang:
    """Guess the language of a message.

    Returns `default` when there is too little alphabetic content to judge —
    "ok", an emoji, or a bare number should not flip a user's language.
    """
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 4:
        return default
    cyrillic = sum(1 for c in letters if _is_cyrillic(c))
    return Lang.RU if cyrillic / len(letters) >= 0.3 else Lang.EN
