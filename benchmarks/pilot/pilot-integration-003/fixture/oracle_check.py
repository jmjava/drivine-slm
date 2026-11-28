"""Pilot oracle: stdlib only; validates answer.txt against spec.json."""
from __future__ import annotations

import json
from pathlib import Path

spec = json.loads(Path("spec.json").read_text(encoding="utf-8"))
name = spec["name"]
label_raw, prop = name.split("_", 1)
label = label_raw[:1].upper() + label_raw[1:]
expected = (
    f"CREATE CONSTRAINT {name} IF NOT EXISTS "
    f"FOR (p:{label}) REQUIRE p.{prop} IS NOT NULL"
)
got = Path("answer.txt").read_text(encoding="utf-8").strip()
if got != expected:
    raise SystemExit(1)
