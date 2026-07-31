"""Crisis screening.

A deliberately blunt keyword pass that runs *before* any model call, in both
languages. It is not a classifier and does not try to be: the cost of a false
positive is one unnecessary signpost to a helpline, and the cost of a false
negative is unacceptable. The model-side escalation flag in the verdict schema
catches the subtler clinical cases; this catches the urgent ones fast.
"""

from __future__ import annotations

import re

_PATTERNS_EN = [
    r"\bkill (?:myself|me)\b",
    r"\bkilling myself\b",
    r"\bend (?:my|it all|my own) (?:life|life\.)?\b",
    r"\bending my life\b",
    r"\btake my own life\b",
    r"\bsuicidal?\b",
    r"\bsuicide\b",
    r"\bwant to die\b",
    r"\bdon'?t want to (?:live|be here|wake up)\b",
    r"\bno reason to (?:live|go on)\b",
    r"\bbetter off dead\b",
    r"\bharm (?:myself|my ?self)\b",
    r"\bhurt(?:ing)? myself\b",
    r"\bcut(?:ting)? myself\b",
    r"\boverdose\b",
]

_PATTERNS_RU = [
    r"\bубить себя\b",
    r"\bсамоубийств",
    r"\bпокончить с собой\b",
    r"\bне хочу жить\b",
    r"\bне хочется жить\b",
    r"\bхочу умереть\b",
    r"\bлучше бы (?:я )?умер",
    r"\bнет смысла жить\b",
    r"\bнавредить себе\b",
    r"\bпричинить себе вред\b",
    r"\bрежу себя\b",
    r"\bсуицид",
]

_COMPILED = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (*_PATTERNS_EN, *_PATTERNS_RU)
]


def is_crisis(text: str) -> bool:
    """True when the message contains an explicit self-harm or suicide signal."""
    return any(pattern.search(text) for pattern in _COMPILED)
