#!/usr/bin/env python3
"""Check the citation corpus before shipping it.

Structural checks always run. With --resolve-doi it also asks doi.org whether
each DOI exists and whether the title on record matches ours — which catches the
one failure mode that would actually embarrass the product: a plausible-looking
reference that does not point at the paper we think it does.

Resolving a DOI is not the same as verifying the finding. Set `verified: true`
on an entry only after a human has read the paper and confirmed that our
one-sentence summary is a fair statement of what it found.

    python scripts/verify_corpus.py
    python scripts/verify_corpus.py --resolve-doi
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from myway.science.library import Library, LibraryError  # noqa: E402

TITLE_MATCH_THRESHOLD = 0.75


def resolve_doi(doi: str) -> tuple[bool, str | None]:
    """Return (exists, title-on-record) for a DOI, via the doi.org content API."""
    request = urllib.request.Request(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/vnd.citationstyles.csl+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False, None
        raise
    title = payload.get("title")
    if isinstance(title, list):
        title = title[0] if title else None
    return True, title


def normalise(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--resolve-doi",
        action="store_true",
        help="check each DOI against doi.org (needs network access)",
    )
    args = parser.parse_args()

    try:
        library = Library()
    except LibraryError as exc:
        print(f"FAIL  corpus is malformed: {exc}")
        return 1

    print(f"OK    corpus loaded: {len(library)} entries, ids unique")

    problems = 0
    missing_doi = [c for c in (library.get(i) for i in library.ids) if not c.doi]
    if missing_doi:
        print(f"WARN  {len(missing_doi)} entr(ies) have no DOI:")
        for citation in missing_doi:
            print(f"        {citation.id}")

    unverified = library.unverified()
    if unverified:
        print(
            f"WARN  {len(unverified)} of {len(library)} entries are not marked "
            "verified — a human must read each paper and confirm our summary:"
        )
        for citation in unverified:
            print(f"        {citation.id}  {citation.reference()}")

    if args.resolve_doi:
        print("\nresolving DOIs against doi.org…")
        checked = 0
        unreachable = 0
        with_doi = sum(1 for cid in library.ids if library.get(cid).doi)
        for cid in library.ids:
            citation = library.get(cid)
            if not citation.doi:
                continue
            try:
                exists, title = resolve_doi(citation.doi)
            except Exception as exc:  # noqa: BLE001 - network is best-effort here
                print(f"WARN  {cid}: could not resolve ({exc})")
                unreachable += 1
                continue
            checked += 1
            if not exists:
                print(f"FAIL  {cid}: DOI {citation.doi} does not resolve")
                problems += 1
                continue
            if title:
                ratio = difflib.SequenceMatcher(
                    None, normalise(citation.title), normalise(title)
                ).ratio()
                if ratio < TITLE_MATCH_THRESHOLD:
                    print(f"FAIL  {cid}: DOI resolves to a different paper")
                    print(f"        ours:   {citation.title}")
                    print(f"        doi.org: {title}")
                    problems += 1
                    continue
            print(f"OK    {cid}")

        # Never report success off the back of checks that did not happen. A
        # blocked network must read as "not verified", not as "verified".
        if checked == 0 and with_doi:
            print(
                f"\nFAIL  asked to resolve {with_doi} DOI(s) and could not reach "
                "doi.org for any of them — nothing was verified. Check network "
                "access or an egress policy, then re-run."
            )
            return 1
        if unreachable:
            print(
                f"\nWARN  {checked}/{with_doi} DOIs resolved; {unreachable} were "
                "unreachable and remain unchecked."
            )

    if problems:
        print(f"\n{problems} problem(s) found.")
        return 1
    print("\nNo blocking problems.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
