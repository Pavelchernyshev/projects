#!/usr/bin/env python3
"""Vault health check.

Enforces the citation contract (docs/citations.md), link integrity, the
freshness policy, and the frontmatter schemas in CLAUDE.md.

Python 3.9+, standard library only. The vault must stay portable: no
dependency should ever be required to check its own integrity.

    python3 scripts/lint.py [--path P] [--orphans] [--json] [--strict]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent

# Directories that hold derived, linkable knowledge.
NOTE_DIRS = ("notes", "topics", "drafts", "projects", "daily")
SKIP_DIRS = {".git", ".obsidian", ".claude", "templates", "docs", "scripts", "node_modules"}
SKIP_FILES = {"CLAUDE.md", "README.md", "index.md", "log.md"}

CITE_RE = re.compile(r"\[(S-\d{8}-[a-z0-9][a-z0-9-]*(?:\s*,\s*S-\d{8}-[a-z0-9-]+)*)\]")
KEY_RE = re.compile(r"S-\d{8}-[a-z0-9][a-z0-9-]*")
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
STAMP_RE = re.compile(r"\(as of (\d{4}-\d{2}(?:-\d{2})?)[^)]*\)")
CODE_FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

# A present-tense claim about something that measurably changes.
VOLATILE_RE = re.compile(
    r"\b(?:has|have|is|are|costs?|stands? at|sits? at|totals?)\s+"
    r"(?:about\s+|around\s+|roughly\s+|~)?"
    r"[\$€£]?\d[\d,.]*\s*"
    r"(?:%|percent|k\b|m\b|bn\b|billion|million|thousand|users|customers|"
    r"employees|stars|forks|subscribers|followers|deals|tickets|open\b)",
    re.I,
)

REQUIRED = {
    "source": ("key", "type", "source_type", "title", "accessed"),
    "note": ("type", "category", "tags", "origin", "created"),
    "topic": ("type", "created"),
    "draft": ("type", "format", "status", "created"),
    "daily": ("type", "date"),
}

ORIGINS = {"ai-distilled", "mine", "mixed"}
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    message: str

    def render(self) -> str:
        loc = f"{self.path}:{self.line}" if self.line else self.path
        return f"  {self.rule:<8} {loc}\n           {self.message}"


@dataclass
class Doc:
    path: Path
    rel: str
    meta: dict
    body: str
    body_offset: int
    cites: set = field(default_factory=set)
    links: set = field(default_factory=set)


def parse_frontmatter(text: str) -> tuple[dict, str, int]:
    """Minimal YAML-subset parser: scalars, inline lists, block lists.

    Deliberately not PyYAML - the vault must be checkable with a bare
    interpreter. Anything this cannot parse is simply absent from the dict,
    which surfaces as a SCHEMA warning rather than a crash.
    """
    if not text.startswith("---"):
        return {}, text, 0
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, 0
    raw = text[3:end]
    body_offset = text[: end + 4].count("\n") + 1
    meta: dict = {}
    key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")) and key:
            item = line.strip().lstrip("-").strip().strip("\"'")
            if item:
                meta.setdefault(key, [])
                if isinstance(meta[key], list):
                    meta[key].append(item)
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()]
        elif value:
            meta[key] = value.strip("\"'")
        else:
            meta[key] = []
    return meta, text[end + 4 :], body_offset


def strip_noise(body: str) -> str:
    """Blank out code, inline code and HTML comments, preserving line numbers."""
    def blank(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    body = CODE_FENCE_RE.sub(blank, body)
    body = HTML_COMMENT_RE.sub(blank, body)
    return INLINE_CODE_RE.sub(blank, body)


def load(vault: Path) -> list[Doc]:
    docs = []
    for path in sorted(vault.rglob("*.md")):
        rel_parts = path.relative_to(vault).parts
        if any(p in SKIP_DIRS for p in rel_parts[:-1]):
            continue
        if len(rel_parts) == 1 and path.name in SKIP_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        meta, body, offset = parse_frontmatter(text)
        doc = Doc(path, str(path.relative_to(vault)), meta, body, offset)
        clean = strip_noise(body)
        for m in CITE_RE.finditer(clean):
            doc.cites.update(KEY_RE.findall(m.group(1)))
        # Links are read from the whole file: `topics:` and `related:` frontmatter
        # entries are real edges, and counting them is what keeps a topic hub from
        # being reported as an orphan.
        doc.links = {m.group(1).strip() for m in LINK_RE.finditer(strip_noise(text))}
        docs.append(doc)
    return docs


def line_of(doc: Doc, needle: str) -> int:
    idx = doc.body.find(needle)
    if idx == -1:
        return 0
    return doc.body_offset + doc.body[:idx].count("\n") + 1


def check(vault: Path, only: Path | None = None) -> tuple[list[Finding], dict]:
    docs = load(vault)
    findings: list[Finding] = []
    add = lambda *a: findings.append(Finding(*a))  # noqa: E731

    sources = {d.meta["key"]: d for d in docs if d.meta.get("key")}
    by_stem = defaultdict(list)
    for d in docs:
        by_stem[d.path.stem.lower()].append(d)

    inbound: dict[str, int] = defaultdict(int)
    for d in docs:
        for target in d.links:
            for hit in by_stem.get(target.lower(), []):
                if hit.rel != d.rel:
                    inbound[hit.rel] += 1

    scoped = [d for d in docs if only is None or d.path == only or only in d.path.parents]

    for d in scoped:
        is_source = d.rel.startswith("sources/")
        doctype = d.meta.get("type", "")

        # --- citation contract -------------------------------------------
        declared = {k for k in d.meta.get("sources", []) if KEY_RE.fullmatch(k)}
        for key in sorted(d.cites):
            if key not in sources:
                rule = "CITE-2" if d.rel.startswith("drafts/") else "CITE-1"
                add(rule, "error", d.rel, line_of(d, key),
                    f"citation {key} resolves to no file in sources/")
            elif key not in declared and doctype in ("note", "draft"):
                add("CITE-3", "warning", d.rel, line_of(d, key),
                    f"{key} cited inline but missing from `sources:` frontmatter")
        for key in sorted(declared - d.cites):
            if key not in sources:
                add("CITE-2", "error", d.rel, 0,
                    f"`sources:` lists {key}, which resolves to no file")

        if is_source and not d.meta.get("key"):
            add("CITE-4", "warning", d.rel, 0, "source file has no `key:`")

        # --- links --------------------------------------------------------
        for target in sorted(d.links):
            if target.lower() not in by_stem:
                add("LINK-1", "error", d.rel, line_of(d, f"[[{target}"),
                    f"wikilink [[{target}]] has no target file")

        # --- freshness ----------------------------------------------------
        dated_container = d.rel.startswith("daily/") or doctype in ("daily", "source")
        if not dated_container:
            clean = strip_noise(d.body)
            for i, raw in enumerate(clean.splitlines(), start=d.body_offset + 1):
                if raw.lstrip().startswith((">", "|")):
                    continue
                if VOLATILE_RE.search(raw) and not STAMP_RE.search(raw):
                    add("FRESH-1", "error", d.rel, i,
                        "volatile claim with no `(as of YYYY-MM-DD)` stamp or pointer: "
                        + raw.strip()[:80])
        for m in STAMP_RE.finditer(d.body):
            stamp = m.group(1)
            try:
                when = dt.date.fromisoformat(stamp if len(stamp) == 10 else stamp + "-01")
            except ValueError:
                continue
            age = (dt.date.today() - when).days
            if age > 180:
                add("FRESH-2", "warning", d.rel, line_of(d, m.group(0)),
                    f"stamp is {age} days old - re-observe, convert to a pointer, or retire")

        # --- schema -------------------------------------------------------
        for f in REQUIRED.get(doctype, ()):
            if not d.meta.get(f):
                add("SCHEMA", "warning", d.rel, 0, f"missing required field `{f}`")
        origin = d.meta.get("origin")
        if doctype == "note" and origin and origin not in ORIGINS:
            add("SCHEMA", "warning", d.rel, 0,
                f"origin `{origin}` is not one of {sorted(ORIGINS)}")

        # --- orphans ------------------------------------------------------
        if d.rel.startswith(("notes/", "topics/")) and inbound[d.rel] == 0:
            add("ORPHAN", "warning", d.rel, 0,
                "no inbound links - nothing in the vault leads here")

    processed = sum(1 for d in docs if d.rel.startswith("sources/") and str(d.meta.get("processed")).lower() == "true")
    total_sources = sum(1 for d in docs if d.rel.startswith("sources/"))
    tags = sorted({t for d in docs for t in d.meta.get("tags", []) if isinstance(t, str)})

    stats = {
        "notes": sum(1 for d in docs if d.rel.startswith("notes/")),
        "topics": sum(1 for d in docs if d.rel.startswith("topics/")),
        "drafts": sum(1 for d in docs if d.rel.startswith("drafts/")),
        "sources": total_sources,
        "sources_processed": processed,
        "backlog": total_sources - processed,
        "tags": tags,
    }
    return findings, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", help="limit checks to one file or directory")
    ap.add_argument("--vault", default=str(VAULT))
    ap.add_argument("--orphans", action="store_true", help="list orphan notes only")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    only = (vault / args.path).resolve() if args.path else None
    findings, stats = check(vault, only)

    if args.orphans:
        orphans = [f for f in findings if f.rule == "ORPHAN"]
        for f in orphans:
            print(f.path)
        return 0

    if args.json:
        print(json.dumps({
            "findings": [f.__dict__ for f in findings],
            "stats": stats,
        }, indent=2))
        return 1 if any(f.severity == "error" for f in findings) else 0

    findings.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.rule, f.path, f.line))
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if errors:
        print(f"\nERRORS ({len(errors)}) - fix before publishing")
        for f in errors:
            print(f.render())
    if warnings:
        print(f"\nWARNINGS ({len(warnings)})")
        for f in warnings:
            print(f.render())
    if not findings:
        print("\nNo findings.")

    print(f"""
VAULT
  notes    {stats['notes']}
  topics   {stats['topics']}
  drafts   {stats['drafts']}
  sources  {stats['sources']}  ({stats['sources_processed']} distilled)
  backlog  {stats['backlog']} captured, not distilled - this is information, not a task
  tags     {len(stats['tags'])}: {', '.join(stats['tags'][:14])}{' ...' if len(stats['tags']) > 14 else ''}
""")

    if errors:
        return 1
    return 1 if (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
