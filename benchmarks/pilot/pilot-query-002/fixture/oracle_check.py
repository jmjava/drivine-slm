"""Pilot oracle: stdlib only; validates answer.txt against people.json."""
from __future__ import annotations

import json
from pathlib import Path

people = json.loads(Path("people.json").read_text(encoding="utf-8"))["people"]
if len(people) != 3 or any(not person.get("name") for person in people):
    raise SystemExit(1)

text = Path("answer.txt").read_text(encoding="utf-8")
for token in ("MATCH", "Person", "RETURN", "count"):
    if token not in text:
        raise SystemExit(1)
if "MERGE" in text:
    raise SystemExit(1)
