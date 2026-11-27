#!/usr/bin/env python3
"""Semantic consistency checks for instruction JSON and JSONL corpora."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JSON = ROOT / "data" / "drivine_instruct.json"
DEFAULT_JSONL = ROOT / "data" / "drivine_instruct.jsonl"

FIELDS = ("instruction", "response", "topic", "id")


def _normalize_row(row: dict, source: str, index: int) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in FIELDS:
        if key not in row:
            raise ValueError(f"{source} row {index}: missing field {key!r}")
        value = row[key]
        if value is None:
            raise ValueError(f"{source} row {index}: field {key!r} is null")
        if not isinstance(value, str):
            raise ValueError(f"{source} row {index}: field {key!r} must be a string")
        if not value.strip():
            raise ValueError(f"{source} row {index}: field {key!r} is empty")
        out[key] = value
    return out


def load_json_rows(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: root must be a JSON array")
    return [_normalize_row(row, str(path), i) for i, row in enumerate(data)]


def load_jsonl_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    rows: list[dict[str, str]] = []
    for i, line in enumerate(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} line {i + 1}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path} line {i + 1}: row must be a JSON object")
        rows.append(_normalize_row(row, f"{path} line {i + 1}", i))
    return rows


def compare_corpora(
    json_rows: list[dict[str, str]],
    jsonl_rows: list[dict[str, str]],
) -> list[str]:
    problems: list[str] = []
    if len(json_rows) != len(jsonl_rows):
        problems.append(
            f"row count mismatch: JSON has {len(json_rows)}, JSONL has {len(jsonl_rows)}"
        )
        return problems

    seen: set[str] = set()
    for i, (j_row, l_row) in enumerate(zip(json_rows, jsonl_rows, strict=True)):
        jid = j_row["id"]
        lid = l_row["id"]
        if jid != lid:
            problems.append(f"row {i}: id order mismatch JSON={jid!r} JSONL={lid!r}")
        if jid in seen:
            problems.append(f"row {i}: duplicate id {jid!r}")
        seen.add(jid)
        for key in FIELDS:
            if j_row[key] != l_row[key]:
                problems.append(
                    f"row {i} id {jid!r}: field {key!r} differs between JSON and JSONL"
                )
    return problems


def check(
    json_path: Path = DEFAULT_JSON,
    jsonl_path: Path = DEFAULT_JSONL,
) -> list[str]:
    problems: list[str] = []
    try:
        json_rows = load_json_rows(json_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"JSON load failed: {exc}"]
    try:
        jsonl_rows = load_jsonl_rows(jsonl_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"JSONL load failed: {exc}"]

    problems.extend(compare_corpora(json_rows, jsonl_rows))
    return problems


def run_self_test() -> list[str]:
    """Verify the checker rejects a deliberate mismatch (temp files only)."""
    failures: list[str] = []
    try:
        json_rows = load_json_rows(DEFAULT_JSON)
        jsonl_rows = load_jsonl_rows(DEFAULT_JSONL)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"self-test setup failed: {exc}"]

    if compare_corpora(json_rows, jsonl_rows):
        failures.append("self-test setup: committed corpora should match before mutation")

    mutated = [dict(r) for r in jsonl_rows]
    if mutated:
        mutated[0] = {**mutated[0], "id": mutated[0]["id"] + "-mismatch"}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        json_copy = tmp_path / "instruct.json"
        jsonl_copy = tmp_path / "instruct.jsonl"
        json_copy.write_text(
            json.dumps([{k: r[k] for k in FIELDS} for r in json_rows], ensure_ascii=False),
            encoding="utf-8",
        )
        with jsonl_copy.open("w", encoding="utf-8") as fh:
            for row in mutated:
                fh.write(
                    json.dumps(
                        {k: row[k] for k in FIELDS},
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        problems = check(json_copy, jsonl_copy)
        if not problems:
            failures.append("self-test: expected mismatch was not detected")
        elif not any("mismatch" in p or "differs" in p or "order" in p for p in problems):
            failures.append(f"self-test: unexpected problem text: {problems!r}")

    good = check(DEFAULT_JSON, DEFAULT_JSONL)
    if good:
        failures.append(f"self-test: committed corpora should pass: {good}")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run negative-case proof in a temp directory",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        failures = run_self_test()
        if failures:
            for msg in failures:
                print(f"check_corpus self-test: {msg}", file=sys.stderr)
            return 1
        print("check_corpus self-test ok")
        return 0

    problems = check(args.json, args.jsonl)
    if problems:
        for msg in problems:
            print(f"check_corpus: {msg}", file=sys.stderr)
        return 1
    print(f"check_corpus ok ({len(load_json_rows(args.json))} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())