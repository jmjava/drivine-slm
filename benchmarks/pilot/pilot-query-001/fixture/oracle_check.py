"""Pilot oracle: stdlib only; validates answer.txt against data.json."""
from __future__ import annotations

import json
from pathlib import Path

values = json.loads(Path("data.json").read_text(encoding="utf-8"))["values"]
expected = str(sum(values))
got = Path("answer.txt").read_text(encoding="utf-8").strip()
if got != expected:
    raise SystemExit(1)