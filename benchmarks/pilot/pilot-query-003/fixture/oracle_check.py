"""Pilot oracle: stdlib only; validates answer.txt against emails.json."""
from __future__ import annotations

import json
from pathlib import Path

people = json.loads(Path("emails.json").read_text(encoding="utf-8"))["people"]
if not people or any("name" not in person or "address" not in person for person in people):
    raise SystemExit(1)
if not any(person["address"] is None for person in people):
    raise SystemExit(1)

text = Path("answer.txt").read_text(encoding="utf-8")
for token in (
    "MATCH",
    "OPTIONAL MATCH",
    "Person",
    "HAS_EMAIL",
    "RETURN",
    "p.name",
    "e.address",
):
    if token not in text:
        raise SystemExit(1)
if "MERGE" in text or "DELETE" in text or "CREATE" in text:
    raise SystemExit(1)
