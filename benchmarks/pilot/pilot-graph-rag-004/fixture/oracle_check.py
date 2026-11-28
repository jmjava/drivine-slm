"""Pilot oracle: stdlib only; validates answer.txt against query.json."""
from __future__ import annotations

import json
from pathlib import Path

spec = json.loads(Path("query.json").read_text(encoding="utf-8"))
answer = Path("answer.txt").read_text(encoding="utf-8")

identifier = spec.get("index")
if identifier is None:
    identifier = spec.get("label")
if identifier is not None and str(identifier) not in answer:
    raise SystemExit(1)

if not any(token in answer for token in ("queryNodes", "fulltext", "embedding")):
    raise SystemExit(1)
