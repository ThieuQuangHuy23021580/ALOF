"""Undo N layers of cp1252/utf-8 double encoding introduced by PowerShell.

PowerShell 5.1's Get-Content -Raw decoded UTF-8 bytes as cp1252, and
Set-Content -Encoding utf8 wrote the resulting mojibake back out.  Each pass
through that pair adds one layer.  This script peels layers until the bytes
decode cleanly as UTF-8 and contain the expected Vietnamese markers.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\MOBILE\FLUTTER\ALOF")
LATEX = ROOT / "docs" / "kltn" / "latex"

TARGETS = [
    LATEX / "chapters" / "02_motivation.tex",
    LATEX / "chapters" / "04_method.tex",
    LATEX / "figures" / "fig_concept_graph_motivation.tex",
    LATEX / "figures" / "fig_temporal_motivation.tex",
]

# Markers that only appear in correctly-decoded Vietnamese text.
GOOD = ["Động lực", "Đặt vấn đề", "Chương", "tương tác", "người học"]
# Markers that appear once corruption has happened.
BAD = ["Ã", "â€", "Â"]

MAX_LAYERS = 6


def peel(data: bytes) -> tuple[bytes, int]:
    """Peel encoding layers until the text looks like clean Vietnamese."""
    for layers in range(MAX_LAYERS + 1):
        text = data.decode("utf-8", errors="replace")
        # Strip any BOM that crept in as literal characters.
        text = text.lstrip("﻿")
        while text[:3] in ("ï»¿", "ï»¿"):
            text = text[3:]
        if layers == 0:
            data = text.encode("utf-8")
        if any(g in text for g in GOOD) and not any(
            text.count(b) > 5 for b in BAD
        ):
            return text.encode("utf-8"), layers
        if layers == MAX_LAYERS:
            break
        # Re-encode the mojibake as cp1252 bytes, then decode as UTF-8.
        try:
            data = text.encode("cp1252", errors="strict")
        except UnicodeEncodeError:
            data = text.encode("cp1252", errors="replace")
    return data, -1


def main() -> int:
    for path in TARGETS:
        if not path.exists():
            print(f"MISSING {path}")
            continue
        raw = path.read_bytes()
        fixed, layers = peel(raw)
        if layers < 0:
            print(f"FAILED   {path} (no clean state found)")
            continue
        path.write_bytes(fixed)
        print(f"OK {layers} layer(s)  {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
