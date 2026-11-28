"""Pilot oracle: stdlib only; validates answer.txt against drop.json."""
from __future__ import annotations

import json
from pathlib import Path

fixture = json.loads(Path("drop.json").read_text(encoding="utf-8"))
answer = Path("answer.txt").read_text(encoding="utf-8")
mutations = ("MERGE", "SET", "DETACH DELETE", "REMOVE")
if (
    str(fixture["id"]) not in answer
    or "CREATE INDEX" in answer
    or not any(op in answer for op in mutations)
):
    raise SystemExit(1)
