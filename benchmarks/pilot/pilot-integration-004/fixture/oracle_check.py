"""Pilot oracle: stdlib only; validates answer.txt against spec.json."""
from __future__ import annotations

import json
from pathlib import Path

spec = json.loads(Path("spec.json").read_text(encoding="utf-8"))
first = spec["stores"][0]
text = Path("answer.txt").read_text(encoding="utf-8")
if "database_type" not in text or first not in text:
    raise SystemExit(1)
