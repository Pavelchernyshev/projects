"""Engine output types.

Kept apart from `engine` so that rendering and tests can import them without
pulling in the Anthropic SDK — the presentation layer has no business depending
on the transport.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Citation


@dataclass
class Probe:
    """One interview decision: ask this, or stop asking."""

    enough_signal: bool
    question: str
    targets_domain: str
    reading: str


@dataclass
class Verdict:
    """The one thing to fix, plus the plan and the evidence behind it."""

    focus_domain: str
    headline: str
    honest_read: str
    why_this_one: str
    not_now: list[str]
    citations: list[Citation]
    action: dict
    escalate_to_professional: bool
    escalation_note: str
    dropped_citation_ids: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        """Persisted form. Citations are stored as ids and re-resolved on read."""
        return {
            "focus_domain": self.focus_domain,
            "headline": self.headline,
            "honest_read": self.honest_read,
            "why_this_one": self.why_this_one,
            "not_now": self.not_now,
            "citation_ids": [c.id for c in self.citations],
            "action": self.action,
            "escalate_to_professional": self.escalate_to_professional,
            "escalation_note": self.escalation_note,
            "dropped_citation_ids": self.dropped_citation_ids,
        }
