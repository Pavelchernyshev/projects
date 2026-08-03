#!/usr/bin/env python3
"""Capture a source into the vault. Zero judgment, one file, done.

The point of this script is that capturing must cost nothing. It never fetches,
never summarizes, never asks. Give it a URL and it writes a file; pipe it a
transcript and the transcript goes in verbatim.

    python3 scripts/capture.py "https://example.com/post" --title "The Post"
    pbpaste | python3 scripts/capture.py "https://youtu.be/xyz" -t "Talk title" --type video
    python3 scripts/capture.py --title "Thought about pricing" --type conversation

Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

VAULT = Path(__file__).resolve().parent.parent

TYPES = ("article", "video", "podcast", "book", "paper", "conversation")

HOST_TYPES = {
    "youtube.com": "video",
    "youtu.be": "video",
    "vimeo.com": "video",
    "arxiv.org": "paper",
    "doi.org": "paper",
    "pubmed.ncbi.nlm.nih.gov": "paper",
    "podcasts.apple.com": "podcast",
    "open.spotify.com": "podcast",
}

STOPWORDS = {"a", "an", "the", "and", "or", "of", "to", "in", "for", "on", "with", "my", "how", "i"}


def slugify(text: str, max_words: int = 5) -> str:
    words = re.sub(r"[^a-z0-9\s-]", " ", text.lower()).split()
    kept = [w for w in words if w not in STOPWORDS] or words
    return "-".join(kept[:max_words]) or "untitled"


def infer_type(url: str) -> str:
    if not url:
        return "conversation"
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for known, kind in HOST_TYPES.items():
        if host == known or host.endswith("." + known):
            return kind
    return "article"


def title_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    tail = path.rsplit("/", 1)[-1] if path else urlparse(url).netloc
    tail = re.sub(r"\.\w{2,5}$", "", tail)
    tail = re.sub(r"[-_]+", " ", tail).strip()
    return tail.title() or urlparse(url).netloc or "Untitled capture"


def mint_key(vault: Path, title: str, today: dt.date) -> str:
    base = f"S-{today:%Y%m%d}-{slugify(title)}"
    existing = {p.stem for p in vault.glob("sources/**/*.md")}
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"


def yaml_str(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?", default="", help="source URL (optional)")
    ap.add_argument("-t", "--title", default="", help="title; inferred from the URL if omitted")
    ap.add_argument("-a", "--author", default="")
    ap.add_argument("--type", dest="source_type", choices=TYPES, help="inferred from the URL if omitted")
    ap.add_argument("--published", default="", help="YYYY-MM-DD, if known")
    ap.add_argument("--tags", default="", help="comma-separated")
    ap.add_argument("--why", default="", help="one line on why this was captured")
    ap.add_argument("--text", default="", help="source text; otherwise read from stdin if piped")
    ap.add_argument("--vault", default=str(VAULT))
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    today = dt.date.today()

    body = args.text
    if not body and not sys.stdin.isatty():
        body = sys.stdin.read()
    body = body.strip()

    title = args.title or (title_from_url(args.url) if args.url else "")
    if not title and body:
        title = body.splitlines()[0].lstrip("# ").strip()[:80]
    if not title:
        ap.error("give a --title, a URL, or piped text to derive one from")

    source_type = args.source_type or infer_type(args.url)
    key = mint_key(vault, title, today)

    out_dir = vault / "sources" / f"{source_type}s"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{key}.md"

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    front = [
        "---",
        f"key: {key}",
        "type: source",
        f"source_type: {source_type}",
        f"title: {yaml_str(title)}",
        f"author: {yaml_str(args.author)}",
        f"url: {yaml_str(args.url)}",
        f"published: {yaml_str(args.published)}",
        f"accessed: {today:%Y-%m-%d}",
        f"tags: [{', '.join(tags)}]",
        "processed: false",
        "notes: []",
        "---",
    ]

    doc = "\n".join(front) + f"\n\n# {title}\n\n## Why captured\n\n{args.why}\n\n## Source text\n\n"
    doc += body if body else "<!-- not yet fetched -->"
    doc += "\n"

    out.write_text(doc, encoding="utf-8")

    log = vault / "log.md"
    if log.exists():
        with log.open("a", encoding="utf-8") as fh:
            fh.write(f"{today:%Y-%m-%d}  capture   {key}\n")

    print(f"{key}\n{out.relative_to(vault)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
