"""Tests for the citation library — the product's honesty guarantee."""

from __future__ import annotations

import pytest
import yaml

from myway.language import detect
from myway.models import Domain, Lang
from myway.science.library import CROSS_CUTTING, Library, LibraryError


@pytest.fixture(scope="module")
def library() -> Library:
    return Library()


def test_corpus_loads_and_covers_every_domain(library: Library) -> None:
    assert len(library) > 0
    for domain in Domain.ordered():
        assert library.for_domain(domain.value), f"no evidence for {domain.value}"
    assert library.for_domain(CROSS_CUTTING), "behaviour-change evidence is required"


def test_every_entry_is_bilingual_and_attributable(library: Library) -> None:
    for cid in library.ids:
        citation = library.get(cid)
        assert citation.finding_en.strip()
        assert citation.finding_ru.strip()
        assert citation.authors.strip()
        assert citation.year > 1950
        assert citation.venue.strip()
        # Findings are folded YAML blocks; loading must produce one clean line.
        assert "\n" not in citation.finding_en
        assert "\n" not in citation.finding_ru


def test_strength_values_are_from_the_known_set(library: Library) -> None:
    allowed = {"strong", "moderate", "suggestive"}
    for cid in library.ids:
        assert library.get(cid).strength in allowed, cid


def test_unknown_ids_are_reported_not_rendered(library: Library) -> None:
    """A model that invents a reference must not be able to show it to a user."""
    real = library.ids[0]
    found, unknown = library.resolve([real, "time.definitelyNotReal2099"])

    assert [c.id for c in found] == [real]
    assert unknown == ["time.definitelyNotReal2099"]


def test_resolve_deduplicates_while_preserving_order(library: Library) -> None:
    a, b = library.ids[0], library.ids[1]
    found, unknown = library.resolve([a, b, a])

    assert [c.id for c in found] == [a, b]
    assert unknown == []


def test_prompt_context_always_appends_behaviour_change(library: Library) -> None:
    context = library.as_prompt_context(["financial"])

    assert "## Domain: financial" in context
    assert f"## Domain: {CROSS_CUTTING}" in context
    # The one-thing-at-a-time evidence must always be selectable.
    assert "change.dalton2012" in context


def test_prompt_context_omits_undiscussed_domains(library: Library) -> None:
    context = library.as_prompt_context(["time"])

    assert "## Domain: time" in context
    assert "## Domain: physical" not in context


def test_reference_line_is_built_from_our_own_fields(library: Library) -> None:
    citation = library.get("social.holtlunstad2010")
    reference = citation.reference()

    assert "Holt-Lunstad" in reference
    assert "2010" in reference
    assert "PLoS Medicine" in reference
    assert "doi:10.1371/journal.pmed.1000316" in reference


def test_russian_findings_are_actually_russian(library: Library) -> None:
    """Guards against an entry that was added with the English text pasted twice."""
    for cid in library.ids:
        citation = library.get(cid)
        assert citation.finding_en != citation.finding_ru, cid
        assert detect(citation.finding_ru) is Lang.RU, cid
        assert detect(citation.finding_en) is Lang.EN, cid


def test_duplicate_ids_are_rejected(tmp_path) -> None:
    entry = {
        "id": "time.dup",
        "authors": "A",
        "year": 2020,
        "title": "T",
        "venue": "V",
        "finding_en": "en",
        "finding_ru": "ru",
    }
    (tmp_path / "a.yaml").write_text(
        yaml.safe_dump({"domain": "time", "entries": [entry]}), encoding="utf-8"
    )
    (tmp_path / "b.yaml").write_text(
        yaml.safe_dump({"domain": "social", "entries": [entry]}), encoding="utf-8"
    )

    with pytest.raises(LibraryError, match="duplicate citation id"):
        Library(tmp_path)


def test_missing_required_field_is_rejected(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text(
        yaml.safe_dump(
            {
                "domain": "time",
                "entries": [{"id": "x", "authors": "A", "year": 2020, "title": "T"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(LibraryError, match="missing"):
        Library(tmp_path)


def test_unknown_domain_is_rejected(tmp_path) -> None:
    (tmp_path / "a.yaml").write_text(
        yaml.safe_dump({"domain": "spiritual", "entries": [{"id": "x"}]}),
        encoding="utf-8",
    )

    with pytest.raises(LibraryError, match="not one of"):
        Library(tmp_path)


def test_empty_corpus_directory_is_rejected(tmp_path) -> None:
    with pytest.raises(LibraryError, match="no corpus files"):
        Library(tmp_path)
