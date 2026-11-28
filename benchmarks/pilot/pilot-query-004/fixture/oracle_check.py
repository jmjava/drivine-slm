"""Pilot oracle: stdlib only; validates answer.txt against nums.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

values = json.loads(Path("nums.json").read_text(encoding="utf-8"))["values"]
text = Path("answer.txt").read_text(encoding="utf-8")
found = [int(token) for token in re.findall(r"\d+", text)]
if found != values:
    raise SystemExit(1)
for token in ("UNWIND", "WITH", "RETURN", "sum"):
    if token not in text:
        raise SystemExit(1)
