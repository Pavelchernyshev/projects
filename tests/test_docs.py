"""Docs that are generated from code must not drift from it.

`docs/sources.md` and `docs/texts-bot.md` are built by `scripts/build_docs.py`.
If someone edits `i18n.py` or the corpus and forgets to regenerate, the docs
start describing a product that no longer exists — so this fails the build
instead of letting it rot.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _load_builder():
    """Import scripts/build_docs.py, which is a script rather than a package."""
    spec = importlib.util.spec_from_file_location(
        "build_docs", ROOT / "scripts" / "build_docs.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_docs"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def builder():
    return _load_builder()


def test_generated_docs_are_current(builder) -> None:
    stale = []
    for name, build in builder.TARGETS.items():
        path = DOCS / name
        assert path.exists(), f"docs/{name} is missing — run scripts/build_docs.py"
        if path.read_text(encoding="utf-8") != build():
            stale.append(name)
    assert not stale, (
        "these generated docs are out of date: "
        + ", ".join(stale)
        + " — run: python scripts/build_docs.py"
    )


def test_every_bot_string_is_documented(builder) -> None:
    """Adding a string to i18n.py forces documenting where the user sees it."""
    from myway.i18n import STRINGS

    undocumented = sorted(set(STRINGS) - set(builder.WHEN_SHOWN))
    assert not undocumented, (
        "add these to WHEN_SHOWN in scripts/build_docs.py: "
        + ", ".join(undocumented)
    )
    orphaned = sorted(set(builder.WHEN_SHOWN) - set(STRINGS))
    assert not orphaned, (
        "these are documented but no longer exist in i18n.py: " + ", ".join(orphaned)
    )


def test_hand_written_docs_exist_and_are_not_stubs() -> None:
    expected = {
        "README.md",
        "product.md",
        "bot-logic.md",
        "texts-landing.md",
        "architecture.md",
        "deploy.md",
    }
    for name in expected:
        path = DOCS / name
        assert path.exists(), f"docs/{name} is missing"
        assert len(path.read_text(encoding="utf-8")) > 800, f"docs/{name} looks empty"


def test_docs_index_links_resolve() -> None:
    """A broken link in the index is the fastest way to make docs useless."""
    import re

    index = (DOCS / "README.md").read_text(encoding="utf-8")
    for target in set(re.findall(r"\]\((?!https?:)([\w./-]+?\.md)", index)):
        assert (DOCS / target).exists(), f"docs/README.md links to missing {target}"
