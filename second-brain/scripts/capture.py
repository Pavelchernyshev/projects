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
import select
import sys
import unicodedata
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

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "for", "on", "with", "my", "how", "i",
    # Russian - this vault captures in both languages
    "и", "в", "во", "на", "с", "со", "по", "для", "о", "об", "к", "из", "от", "как", "что",
}

# Cyrillic to Latin, so a Russian title produces a meaningful key instead of
# "untitled". Keys are permanent and get cited, so they have to be readable.
CYRILLIC = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e",
    "ю": "yu", "я": "ya",
    # Ukrainian / Belarusian extras
    "і": "i", "ї": "yi", "є": "ye", "ґ": "g", "ў": "u",
}


def detect_lang(*parts: str) -> str:
    """Cheap script check: Cyrillic-heavy means Russian, else English.

    Deliberately a heuristic and deliberately overridable with --lang. Getting
    this wrong costs one frontmatter field; blocking a capture to ask would cost
    the capture.
    """
    text = " ".join(parts)
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "en"
    cyrillic = sum(1 for c in letters if "\u0400" <= c <= "\u04ff")
    return "ru" if cyrillic / len(letters) > 0.2 else "en"


def translit(text: str) -> str:
    """Fold any script down to ASCII: accents stripped, Cyrillic transliterated."""
    out = []
    for ch in text.lower():
        if ch in CYRILLIC:
            out.append(CYRILLIC[ch])
        else:
            # NFKD splits an accented letter into base + combining mark; drop the mark.
            decomposed = unicodedata.normalize("NFKD", ch)
            out.append("".join(c for c in decomposed if not unicodedata.combining(c)))
    return "".join(out)


def slugify(text: str, max_words: int = 5) -> str:
    lowered = text.lower()
    words = re.sub(r"[^a-z0-9\s-]", " ", translit(lowered)).split()
    # Filter stopwords in the original script too, since translit turns "и" into "i".
    original = re.sub(r"[^\w\s-]", " ", lowered, flags=re.U).split()
    if len(original) == len(words):
        words = [w for w, o in zip(words, original) if o not in STOPWORDS] or words
    else:
        words = [w for w in words if w not in STOPWORDS] or words
    return "-".join(words[:max_words]) or "untitled"


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


def read_piped_text(force: bool, wait: float = 0.25) -> str:
    """Read stdin only when something is actually there.

    A bare `sys.stdin.read()` guarded by `isatty()` hangs forever when stdin is
    an inherited pipe that nobody writes to and nobody closes - which is what
    happens under cron, CI, and most agent shells. Capture must never block:
    a capture lane that can hang is a capture lane you stop trusting.

    `--stdin` forces a full blocking read for a slow producer (curl, a long
    pipeline). Otherwise we poll briefly and move on.
    """
    if force:
        return sys.stdin.read()
    if sys.stdin.isatty():
        return ""
    try:
        ready, _, _ = select.select([sys.stdin], [], [], wait)
    except (OSError, ValueError):  # not selectable on this platform/handle
        return ""
    return sys.stdin.read() if ready else ""


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
    ap.add_argument("--lang", choices=("en", "ru"), help="source language; detected if omitted")
    ap.add_argument("--why", default="", help="one line on why this was captured")
    ap.add_argument("--text", default="", help="source text; otherwise read from stdin if piped")
    ap.add_argument("--stdin", action="store_true",
                    help="force a blocking read of stdin (use with a slow producer)")
    ap.add_argument("--vault", default=str(VAULT))
    args = ap.parse_args()

    vault = Path(args.vault).resolve()
    today = dt.date.today()

    body = (args.text or read_piped_text(args.stdin)).strip()

    title = args.title or (title_from_url(args.url) if args.url else "")
    if not title and body:
        title = body.splitlines()[0].lstrip("# ").strip()[:80]
    if not title:
        ap.error("give a --title, a URL, or piped text to derive one from")

    source_type = args.source_type or infer_type(args.url)
    lang = args.lang or detect_lang(title, body[:4000])
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
        f"lang: {lang}",
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
