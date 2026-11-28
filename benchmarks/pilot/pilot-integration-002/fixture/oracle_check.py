"""Pilot oracle: stdlib only; validates answer.txt against spec.json."""
from __future__ import annotations

import json
from pathlib import Path

spec = json.loads(Path("spec.json").read_text(encoding="utf-8"))
label = spec["label"]
prop = spec["prop"]
expected = (
    f"CREATE CONSTRAINT {label.lower()}_{prop} IF NOT EXISTS "
    f"FOR (p:{label}) REQUIRE p.{prop} IS UNIQUE"
)
got = Path("answer.txt").read_text(encoding="utf-8").strip()
if got != expected:
    raise SystemExit(1)
