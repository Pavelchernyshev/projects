"""Tests for i18n coverage, language detection, safety screening, and rendering."""

from __future__ import annotations

import pytest

from myway import render, safety
from myway.coach.results import Verdict
from myway.i18n import DOMAIN_HINT, DOMAIN_ICON, DOMAIN_LABEL, STRINGS, t
from myway.language import detect
from myway.models import Domain, Lang
from myway.science import Library

# --- i18n ------------------------------------------------------------------


def test_every_string_exists_in_both_languages() -> None:
    for key, translations in STRINGS.items():
        assert Lang.EN in translations, f"{key} is missing English"
        assert Lang.RU in translations, f"{key} is missing Russian"
        assert translations[Lang.EN].strip(), key
        assert translations[Lang.RU].strip(), key


def test_placeholders_match_across_languages() -> None:
    import re

    for key, translations in STRINGS.items():
        placeholders = {
            lang: set(re.findall(r"\{(\w+)\}", text))
            for lang, text in translations.items()
        }
        assert placeholders[Lang.EN] == placeholders[Lang.RU], (
            f"{key}: placeholder mismatch {placeholders}"
        )


def test_every_domain_has_a_label_hint_and_icon() -> None:
    for domain in Domain.ordered():
        for lang in (Lang.EN, Lang.RU):
            assert DOMAIN_LABEL[domain][lang].strip()
            assert DOMAIN_HINT[domain][lang].strip()
        assert DOMAIN_ICON[domain]


def test_missing_translation_raises_rather_than_silently_blanking() -> None:
    with pytest.raises(KeyError, match="missing translation"):
        t("no_such_key", Lang.EN)


# --- language detection ----------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        ("I keep putting off dealing with my sleep", Lang.EN),
        ("Я всё время откладываю разговор с руководителем", Lang.RU),
        ("Мой sleep schedule полностью развалился", Lang.RU),  # mixed, mostly RU
        ("My расписание is broken but mostly I write in English", Lang.EN),
    ],
)
def test_detects_language_from_prose(text: str, expected: Lang) -> None:
    assert detect(text) is expected


@pytest.mark.parametrize("text", ["", "ok", "5", "👍", "   "])
def test_short_or_wordless_input_keeps_the_default(text: str) -> None:
    assert detect(text, default=Lang.RU) is Lang.RU
    assert detect(text, default=Lang.EN) is Lang.EN


# --- safety ----------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "honestly I want to die",
        "I've been thinking about killing myself",
        "sometimes I feel suicidal",
        "there is no reason to live anymore",
        "я не хочу жить",
        "думаю о самоубийстве",
        "иногда хочу умереть",
    ],
)
def test_crisis_language_is_caught(text: str) -> None:
    assert safety.is_crisis(text)


@pytest.mark.parametrize(
    "text",
    [
        "my job is killing me slowly",
        "I'd die for a proper holiday",
        "this deadline is murder",
        "работа меня убивает",
        "я живу как будто на автопилоте",
        "I want to live differently",
    ],
)
def test_ordinary_hyperbole_is_not_flagged(text: str) -> None:
    assert not safety.is_crisis(text)


# --- rendering -------------------------------------------------------------


def _verdict(**overrides) -> Verdict:
    library = Library()
    base = {
        "focus_domain": "mental",
        "headline": "Your sleep debt is the thing driving everything else",
        "honest_read": "You called it 'just being busy' four times.",
        "why_this_one": "Fix sleep and the other four get easier.",
        "not_now": ["time", "financial"],
        "citations": [library.get("mental.cappuccio2010")],
        "action": {
            "if_then": "If it is 23:30, then I put my phone on the kitchen counter.",
            "obstacle": "You will want to finish one more episode.",
            "if_obstacle_then": "If the episode is not finished, I stop it anyway.",
            "first_rep_when": "Tonight, 23:30",
            "cadence": "Every weeknight",
            "measure": "Nights the phone left the bedroom, counted on Sunday",
        },
        "escalate_to_professional": False,
        "escalation_note": "",
        "dropped_citation_ids": [],
    }
    base.update(overrides)
    return Verdict(**base)


def test_verdict_renders_diagnosis_plan_and_evidence() -> None:
    messages = render.verdict_messages(_verdict(), Lang.EN)

    assert len(messages) == 3
    assert "The one thing" in messages[0]
    assert "sleep debt" in messages[0]
    assert "Not now:" in messages[0]
    assert "kitchen counter" in messages[1]
    assert "Cappuccio" in messages[2]
    assert "doi:10.1093/sleep/33.5.585" in messages[2]


def test_escalation_is_surfaced_before_the_plan() -> None:
    messages = render.verdict_messages(
        _verdict(escalate_to_professional=True, escalation_note="This looks clinical."),
        Lang.EN,
    )

    assert "This looks clinical." in messages[1]
    assert "professional" in messages[1]
    assert "kitchen counter" in messages[2]


def test_model_written_text_cannot_inject_markup() -> None:
    messages = render.verdict_messages(
        _verdict(headline="You <b>said</b> it & meant it"), Lang.EN
    )

    assert "&lt;b&gt;said&lt;/b&gt;" in messages[0]
    assert "&amp; meant it" in messages[0]


def test_a_verdict_with_no_citations_still_renders() -> None:
    messages = render.verdict_messages(_verdict(citations=[]), Lang.EN)

    assert len(messages) == 2


def test_messages_stay_within_telegram_limits() -> None:
    long_read = "x" * 9000
    messages = render.verdict_messages(_verdict(honest_read=long_read), Lang.EN)

    for message in messages:
        assert len(message) <= render.MAX_MESSAGE


def test_russian_verdict_uses_russian_findings() -> None:
    messages = render.verdict_messages(_verdict(), Lang.RU)

    assert "Одна вещь" in messages[0]
    assert "продолжительность сна" in messages[2]


def test_sources_listing_covers_the_library_and_fits_telegram() -> None:
    library = Library()
    messages = render.sources_messages(library, Lang.EN)

    combined = "\n".join(messages)
    for message in messages:
        assert len(message) <= render.MAX_MESSAGE
    for cid in library.ids:
        citation = library.get(cid)
        assert render.esc(citation.authors) in combined, cid
