from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from drivine_runner.constants import (
    DRIVINE_DOMAIN,
    REGISTERED_DRIVINE_AREAS,
    REQUIRED_TASK_KEYS,
    TASK_SPEC_VERSION,
)
from drivine_runner.paths import (
    PathSafetyError,
    assert_no_duplicate_paths,
    validate_relative_path,
)


class TaskSpecError(ValueError):
    pass


@dataclass(frozen=True)
class FileCheck:
    type: str
    path: str
    expected_sha256: str | None = None
    expected_content: str | None = None


@dataclass(frozen=True)
class TaskPins:
    source: str
    package: str


@dataclass(frozen=True)
class TaskSpec:
    raw_path: Path
    task_spec_version: str
    task_id: str
    domain: str
    area: str
    prompt: str
    answer_language: str
    expected_output_files: tuple[str, ...]
    fixture_dir: str
    oracle_argv: tuple[str, ...]
    timeout_seconds: float
    pins: TaskPins
    checks: tuple[FileCheck, ...]

    @property
    def fixture_path(self) -> Path:
        return self.raw_path.parent / self.fixture_dir


def _require_str(obj: dict[str, Any], key: str) -> str:
    val = obj.get(key)
    if not isinstance(val, str) or not val.strip():
        raise TaskSpecError(f"{key} must be a non-empty string")
    return val


def _require_number(obj: dict[str, Any], key: str) -> float:
    val = obj.get(key)
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        raise TaskSpecError(f"{key} must be a number")
    if val <= 0:
        raise TaskSpecError(f"{key} must be positive")
    return float(val)


def _validate_checks(raw: Any) -> tuple[FileCheck, ...]:
    if not isinstance(raw, list):
        raise TaskSpecError("checks must be a list")
    out: list[FileCheck] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise TaskSpecError(f"checks[{i}] must be an object")
        unknown = set(item) - {"type", "path", "expected_sha256", "expected_content"}
        if unknown:
            raise TaskSpecError(f"checks[{i}] has unknown fields: {sorted(unknown)}")
        ctype = item.get("type")
        if ctype not in ("file_equals", "file_sha256"):
            raise TaskSpecError(f"checks[{i}].type must be file_equals or file_sha256")
        path = validate_relative_path(_require_str(item, "path"), label="checks.path")
        sha = item.get("expected_sha256")
        content = item.get("expected_content")
        if ctype == "file_sha256":
            if not isinstance(sha, str) or len(sha) != 64:
                raise TaskSpecError(f"checks[{i}] requires expected_sha256 (64 hex chars)")
        if ctype == "file_equals":
            if not isinstance(content, str):
                raise TaskSpecError(f"checks[{i}] requires expected_content string")
        out.append(
            FileCheck(
                type=ctype,
                path=path,
                expected_sha256=sha if isinstance(sha, str) else None,
                expected_content=content if isinstance(content, str) else None,
            )
        )
    return tuple(out)


def validate_task_dict(data: dict[str, Any], *, task_path: Path | None = None) -> TaskSpec:
    if not isinstance(data, dict):
        raise TaskSpecError("task spec must be a JSON object")

    unknown = set(data) - REQUIRED_TASK_KEYS
    if unknown:
        raise TaskSpecError(f"unknown task fields: {sorted(unknown)}")

    missing = REQUIRED_TASK_KEYS - set(data)
    if missing:
        raise TaskSpecError(f"missing task fields: {sorted(missing)}")

    version = _require_str(data, "task_spec_version")
    if version != TASK_SPEC_VERSION:
        raise TaskSpecError(
            f"unsupported task_spec_version {version!r} (expected {TASK_SPEC_VERSION!r})"
        )

    domain = _require_str(data, "domain")
    if domain != DRIVINE_DOMAIN:
        raise TaskSpecError(f"domain must be {DRIVINE_DOMAIN!r}")

    area = _require_str(data, "area")
    if area not in REGISTERED_DRIVINE_AREAS:
        raise TaskSpecError(
            f"area {area!r} not in registered Drivine areas: {sorted(REGISTERED_DRIVINE_AREAS)}"
        )

    raw_outputs = data["expected_output_files"]
    if not isinstance(raw_outputs, list) or not raw_outputs:
        raise TaskSpecError("expected_output_files must be a non-empty list of strings")
    outputs: list[str] = []
    for i, entry in enumerate(raw_outputs):
        if not isinstance(entry, str):
            raise TaskSpecError(f"expected_output_files[{i}] must be a string")
        try:
            outputs.append(validate_relative_path(entry, label="expected_output_files"))
        except PathSafetyError as exc:
            raise TaskSpecError(str(exc)) from exc
    assert_no_duplicate_paths(outputs)

    fixture_dir = validate_relative_path(_require_str(data, "fixture_dir"), label="fixture_dir")

    oracle = data["oracle_argv"]
    if not isinstance(oracle, list) or not oracle:
        raise TaskSpecError("oracle_argv must be a non-empty array")
    if not all(isinstance(x, str) and x for x in oracle):
        raise TaskSpecError("oracle_argv entries must be non-empty strings")
    oracle_tuple = tuple(oracle)

    pins_raw = data["pins"]
    if not isinstance(pins_raw, dict):
        raise TaskSpecError("pins must be an object")
    pin_unknown = set(pins_raw) - {"source", "package"}
    if pin_unknown:
        raise TaskSpecError(f"pins has unknown fields: {sorted(pin_unknown)}")
    pins = TaskPins(
        source=_require_str(pins_raw, "source"),
        package=_require_str(pins_raw, "package"),
    )

    checks = _validate_checks(data["checks"])

    spec = TaskSpec(
        raw_path=task_path or Path("task.json"),
        task_spec_version=version,
        task_id=_require_str(data, "task_id"),
        domain=domain,
        area=area,
        prompt=_require_str(data, "prompt"),
        answer_language=_require_str(data, "answer_language"),
        expected_output_files=tuple(outputs),
        fixture_dir=fixture_dir,
        oracle_argv=oracle_tuple,
        timeout_seconds=_require_number(data, "timeout_seconds"),
        pins=pins,
        checks=checks,
    )

    if task_path is not None:
        fx = spec.fixture_path
        if not fx.is_dir():
            raise TaskSpecError(f"fixture_dir not found: {fx}")

    return spec


def load_task_spec(path: Path) -> TaskSpec:
    path = path.resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TaskSpecError(f"invalid JSON in {path}: {exc}") from exc
    return validate_task_dict(data, task_path=path)