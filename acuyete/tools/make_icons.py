#!/usr/bin/env python3
"""Иконка приложения: то же поле света на чёрном, что и внутри магазина.

PNG пишется руками через zlib — Pillow ради трёх кругов ставить не нужно, а
иконки должны пересобираться на любой машине без установки зависимостей.

    python3 acuyete/tools/make_icons.py
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "icons"

BASE = (8, 8, 9)
# Те же три пятна, что у ОБЪЕКТА 01 «ТИХОЕ» в data.js: иконка — его портрет.
BLOBS = (
    ((0.50, 0.46), 0.52, (236, 226, 208), 1.00),
    ((0.38, 0.60), 0.42, (176, 168, 178), 0.55),
    ((0.63, 0.61), 0.38, (120, 112, 124), 0.50),
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
    """spread < 1 сжимает рисунок к центру — это нужно маскируемой иконке,
    у которой Android срезает края под форму лаунчера."""
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
                # мягкий спад: без него пятно читается как диск, а не как свет
                a = peak * (1 - d) ** 1.9
                r += colour[0] * a
                g += colour[1] * a
                b += colour[2] * a
            # виньетка от центра к краю
            edge = math.hypot(u - 0.5, v - 0.5) / 0.72
            k = max(0.0, 1 - 0.55 * min(1.0, edge) ** 2)
            row += bytes(
                (min(255, int(c * k)) for c in (r, g, b))
            )
        rows.append(row)
    return _png(size, size, rows)


MARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#08080a"/>
  <defs>
    <radialGradient id="a" cx="50%" cy="44%" r="46%">
      <stop offset="0" stop-color="#ece2d0" stop-opacity=".72"/>
      <stop offset="1" stop-color="#ece2d0" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="b" cx="36%" cy="60%" r="38%">
      <stop offset="0" stop-color="#b0a8b2" stop-opacity=".45"/>
      <stop offset="1" stop-color="#b0a8b2" stop-opacity="0"/>
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
