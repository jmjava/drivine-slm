"""Pilot oracle: stdlib only; validates a repaired query in answer.txt."""
from __future__ import annotations

from pathlib import Path

broken = Path("broken.cypher").read_text(encoding="utf-8")
got = Path("answer.txt").read_text(encoding="utf-8")
if got.strip() == broken.strip():
    raise SystemExit(1)
if "'Alice'" not in got:
    raise SystemExit(1)
