"""Pilot oracle: stdlib only; validates a repaired query in answer.txt."""
from __future__ import annotations

import json
from pathlib import Path

broken = Path("broken.cypher").read_text(encoding="utf-8")
got = Path("answer.txt").read_text(encoding="utf-8")
age = json.loads(Path("params.json").read_text(encoding="utf-8"))["age"]
if got.strip() == broken.strip():
    raise SystemExit(1)
if str(age) not in got:
    raise SystemExit(1)
