#!/usr/bin/env python3
"""One file, for a preview link.

The product is five modules and a stylesheet served over http. For a link
someone can open on a phone without a server — a hosted preview, a mail — this
folds them into a single HTML file: the stylesheet inline, the modules wrapped
in their own scopes so nothing collides, the service worker and manifest left
out (a preview has no install story).

    python3 ohuet/tools/bundle.py > ohuet-preview.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# module → what it hands to the others
EXPORTS = {
    "data.js": ["STATE", "LINES", "SHIRT", "WORD", "WORD_SETTLE_MS", "WORD_STAY_MS", "FIRST_LINE_AFTER_MS", "LINE_EVERY_MS"],
    "object.js": ["mountObject"],
    "glass.js": ["mountGlass"],
    "sound.js": ["start", "stop", "isOn"],
}


def module(name: str) -> str:
    src = (ROOT / name).read_text(encoding="utf-8")
    src = re.sub(r"^import[^\n]*\n(?:[^\n]*\n)*?[^\n]*from\s+\"[^\"]+\";\n", "", src, flags=re.M)  # multi-line imports
    src = re.sub(r"^import[^\n]*;\n", "", src, flags=re.M)
    src = re.sub(r"^export\s+(async\s+)?function", r"\1function", src, flags=re.M)
    src = re.sub(r"^export\s+const", "const", src, flags=re.M)
    return src


def main() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "app.css").read_text(encoding="utf-8")
    body = html.split("<body", 1)[1]
    body = body.split(">", 1)[1]
    body = body.rsplit("</body>", 1)[0]
    body = re.sub(r"<script[^>]*src=\"./app.js\"[^>]*></script>\s*", "", body)

    parts = []
    for name, names in EXPORTS.items():
        parts.append(
            f"const __{name[:-3]} = (() => {{\n{module(name)}\nreturn {{ {', '.join(names)} }};\n}})();"
        )
    app = module("app.js")
    app = app.replace('navigator.serviceWorker.register("./sw.js")', "Promise.reject(new Error('preview'))")
    head = (
        "const { STATE, LINES, SHIRT, WORD, WORD_SETTLE_MS, WORD_STAY_MS, FIRST_LINE_AFTER_MS, LINE_EVERY_MS } = __data;\n"
        "const { mountObject } = __object;\nconst { mountGlass } = __glass;\nconst voice = __sound;\n"
    )
    parts.append("(() => {\n" + head + app + "\n})();")
    script = "\n\n".join(parts)

    out = (
        "<title>OHUET, carried</title>\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="color-scheme" content="light">\n'
        f"<style>\n{css}\n</style>\n"
        f"{body.strip()}\n"
        f'<script type="module">\n{script}\n</script>\n'
    )
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
