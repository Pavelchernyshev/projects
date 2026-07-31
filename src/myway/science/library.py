"""The curated citation library.

This module is the product's honesty guarantee. The model never writes a
reference: it selects citation *ids* from a list we hand it, and we render the
bibliographic detail from YAML ourselves. An id the model invents fails lookup
and is dropped, so a fabricated reference cannot reach a user.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ..models import Citation, Domain

CORPUS_DIR = Path(__file__).parent / "corpus"

# Behaviour-change evidence is not one of the five wealth domains — it is always
# in scope, because every verdict ends in a plan.
CROSS_CUTTING = "cross_cutting"

_REQUIRED_FIELDS = (
    "id",
    "authors",
    "year",
    "title",
    "venue",
    "finding_en",
    "finding_ru",
)


class LibraryError(RuntimeError):
    """Raised when the corpus on disk is malformed."""


class Library:
    """Loads and indexes the vetted corpus."""

    def __init__(self, corpus_dir: Path | None = None) -> None:
        self._dir = corpus_dir or CORPUS_DIR
        self._by_id: dict[str, Citation] = {}
        self._by_domain: dict[str, list[Citation]] = {}
        self._use_when: dict[str, str] = {}
        self._tags: dict[str, list[str]] = {}
        self._load()

    # --- loading -----------------------------------------------------------

    def _load(self) -> None:
        files = sorted(self._dir.glob("*.yaml"))
        if not files:
            raise LibraryError(f"no corpus files found in {self._dir}")

        for path in files:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            domain = data.get("domain")
            if not domain:
                raise LibraryError(f"{path.name}: missing top-level 'domain'")

            known = {d.value for d in Domain} | {CROSS_CUTTING}
            if domain not in known:
                raise LibraryError(
                    f"{path.name}: domain {domain!r} is not one of {sorted(known)}"
                )

            entries = data.get("entries") or []
            if not entries:
                raise LibraryError(f"{path.name}: no entries")

            for entry in entries:
                missing = [f for f in _REQUIRED_FIELDS if not entry.get(f)]
                if missing:
                    raise LibraryError(
                        f"{path.name}: entry {entry.get('id', '<no id>')} "
                        f"missing {', '.join(missing)}"
                    )
                cid = entry["id"]
                if cid in self._by_id:
                    raise LibraryError(f"duplicate citation id {cid!r}")

                citation = Citation(
                    id=cid,
                    authors=entry["authors"],
                    year=int(entry["year"]),
                    title=entry["title"],
                    venue=entry["venue"],
                    finding_en=_squash(entry["finding_en"]),
                    finding_ru=_squash(entry["finding_ru"]),
                    doi=entry.get("doi"),
                    design=entry.get("design"),
                    strength=entry.get("strength", "moderate"),
                    verified=bool(entry.get("verified", False)),
                )
                self._by_id[cid] = citation
                self._by_domain.setdefault(domain, []).append(citation)
                self._use_when[cid] = entry.get("use_when", "")
                self._tags[cid] = list(entry.get("tags") or [])

    # --- access ------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._by_id)

    @property
    def ids(self) -> list[str]:
        return list(self._by_id)

    def get(self, citation_id: str) -> Citation | None:
        return self._by_id.get(citation_id)

    def for_domain(self, domain: str) -> list[Citation]:
        return list(self._by_domain.get(domain, []))

    def resolve(self, citation_ids: list[str]) -> tuple[list[Citation], list[str]]:
        """Split model-supplied ids into (found citations, unknown ids).

        Unknown ids are the fabrication signal: they get logged and dropped
        rather than shown, so a hallucinated reference never reaches a user.
        """
        found: list[Citation] = []
        unknown: list[str] = []
        seen: set[str] = set()
        for cid in citation_ids:
            if cid in seen:
                continue
            seen.add(cid)
            citation = self._by_id.get(cid)
            if citation is None:
                unknown.append(cid)
            else:
                found.append(citation)
        return found, unknown

    def unverified(self) -> list[Citation]:
        """Entries a human has not yet checked against the source of record."""
        return [c for c in self._by_id.values() if not c.verified]

    # --- prompt rendering --------------------------------------------------

    def as_prompt_context(self, domains: list[str]) -> str:
        """Render the selectable evidence for the given domains.

        Cross-cutting behaviour-change evidence is always appended, because
        every verdict ends in a plan and the plan needs its own grounding.
        """
        wanted = list(dict.fromkeys([*domains, CROSS_CUTTING]))
        lines: list[str] = []
        for domain in wanted:
            citations = self._by_domain.get(domain)
            if not citations:
                continue
            lines.append(f"## Domain: {domain}")
            for citation in citations:
                lines.append(f"- id: {citation.id}")
                lines.append(f"  claim: {citation.finding_en}")
                lines.append(
                    f"  evidence: {citation.design or 'see source'} "
                    f"(strength: {citation.strength})"
                )
                if self._use_when[citation.id]:
                    lines.append(f"  use_when: {self._use_when[citation.id]}")
            lines.append("")
        return "\n".join(lines).strip()


def _squash(text: str) -> str:
    """Collapse YAML folded-block whitespace into a single clean paragraph."""
    return " ".join(text.split())
