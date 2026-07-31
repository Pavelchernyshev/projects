"""Domain objects shared across the bot, coach engine, and storage layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Domain(StrEnum):
    """The five types of wealth this product is built around.

    Taxonomy follows Sahil Bloom's "The 5 Types of Wealth" (2025). The labels
    are ours; the evidence behind each one lives in `science/corpus/`.
    """

    TIME = "time"
    SOCIAL = "social"
    MENTAL = "mental"
    PHYSICAL = "physical"
    FINANCIAL = "financial"

    @classmethod
    def ordered(cls) -> list[Domain]:
        return [cls.TIME, cls.SOCIAL, cls.MENTAL, cls.PHYSICAL, cls.FINANCIAL]


class State(StrEnum):
    """Where a session sits in the interview.

    The transition table lives in `coach.flow`; this enum is only the label.
    """

    ONBOARDING = "onboarding"
    OPENING = "opening"      # one open question, in the user's own words
    PULSE = "pulse"          # 1-5 rating for each of the five domains
    PROBE = "probe"          # adaptive follow-ups on the weakest domain
    VERDICT = "verdict"      # the one thing to fix, with citations
    COMMIT = "commit"        # a single concrete action + a check-in date
    IDLE = "idle"            # between sessions


class Lang(StrEnum):
    RU = "ru"
    EN = "en"


@dataclass
class Turn:
    """One utterance in the interview transcript."""

    role: str            # "coach" | "user"
    text: str
    kind: str = "text"   # "text" | "voice"
    domain: str | None = None
    created_at: datetime | None = None


@dataclass
class Session:
    id: int | None
    user_id: int
    state: State = State.ONBOARDING
    lang: Lang = Lang.EN
    pulse: dict[str, int] = field(default_factory=dict)
    focus_domain: str | None = None
    probe_count: int = 0
    transcript: list[Turn] = field(default_factory=list)
    verdict: dict | None = None
    commitment: dict | None = None

    def weakest_domains(self) -> list[str]:
        """Domains sorted worst-first by pulse score, ties keeping canonical order."""
        order = {d.value: i for i, d in enumerate(Domain.ordered())}
        scored = [(score, order[name], name) for name, score in self.pulse.items()]
        return [name for _, _, name in sorted(scored)]

    def pending_pulse_domain(self) -> Domain | None:
        """Next domain still awaiting a rating, or None when the pulse is done."""
        for domain in Domain.ordered():
            if domain.value not in self.pulse:
                return domain
        return None


@dataclass
class Citation:
    """A vetted reference. Rendered from the corpus, never from model output."""

    id: str
    authors: str
    year: int
    title: str
    venue: str
    finding_en: str
    finding_ru: str
    doi: str | None = None
    design: str | None = None
    strength: str = "moderate"   # strong | moderate | suggestive
    verified: bool = False

    def reference(self) -> str:
        """The bibliographic line, rendered from our own data — never the model's."""
        source = f"{self.authors} ({self.year}). {self.title}. {self.venue}"
        if self.doi:
            source += f". doi:{self.doi}"
        return source
