#!/usr/bin/env python3
"""The app icon: the same field of light as the state itself.

The PNG is written by hand through zlib — Pillow is not worth installing for
three circles, and the icons must rebuild on any machine with nothing added.

    python3 ohuet/tools/make_icons.py
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "icons"

BASE = (7, 7, 8)
# The three lights from STATE in data.js — stone, the moss, mineral — at rest.
BLOBS = (
    ((0.50, 0.46), 0.52, (224, 212, 192), 1.00),
    ((0.38, 0.60), 0.42, (150, 168, 142), 0.42),
    ((0.63, 0.61), 0.38, (104, 90, 84), 0.60),
)


def _png(width: int, height: int, rows: list[bytearray]) -> bytes:
    raw = b"".join(b"\x00" + bytes(row) for row in rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def render(size: int, spread: float = 1.0) -> bytes:
    """spread < 1 pulls the drawing toward the centre — the maskable icon needs
    it, since Android crops the edges to the launcher shape."""
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            u, v = (x + 0.5) / size, (y + 0.5) / size
            r, g, b = BASE
            for (cx, cy), radius, colour, peak in BLOBS:
                cx = 0.5 + (cx - 0.5) * spread
                cy = 0.5 + (cy - 0.5) * spread
                d = math.hypot(u - cx, v - cy) / (radius * spread)
                if d >= 1:
                    continue
                # soft falloff: without it the spot reads as a disc, not light
                a = peak * (1 - d) ** 1.9
                r += colour[0] * a
                g += colour[1] * a
                b += colour[2] * a
            # vignette, centre to edge
            edge = math.hypot(u - 0.5, v - 0.5) / 0.72
            k = max(0.0, 1 - 0.55 * min(1.0, edge) ** 2)
            row += bytes(
                (min(255, int(c * k)) for c in (r, g, b))
            )
        rows.append(row)
    return _png(size, size, rows)


MARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#070708"/>
  <defs>
    <radialGradient id="a" cx="50%" cy="44%" r="46%">
      <stop offset="0" stop-color="#e0d4c0" stop-opacity=".72"/>
      <stop offset="1" stop-color="#e0d4c0" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="b" cx="36%" cy="60%" r="38%">
      <stop offset="0" stop-color="#96a88e" stop-opacity=".3"/>
      <stop offset="1" stop-color="#96a88e" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="512" height="512" fill="url(#a)"/>
  <rect width="512" height="512" fill="url(#b)"/>
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "icon-192.png").write_bytes(render(192))
    (OUT / "icon-512.png").write_bytes(render(512))
    (OUT / "icon-maskable-512.png").write_bytes(render(512, spread=0.72))
    (OUT / "apple-touch-icon.png").write_bytes(render(180))
    (OUT / "mark.svg").write_text(MARK_SVG, encoding="utf-8")
    for f in sorted(OUT.iterdir()):
        print(f"{f.name}: {f.stat().st_size} B")


if __name__ == "__main__":
    main()
