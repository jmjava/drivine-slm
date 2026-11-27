from __future__ import annotations

import os
from pathlib import Path, PurePosixPath


class PathSafetyError(ValueError):
    pass


def _is_safe_relative(rel: str) -> bool:
    if not rel or rel.strip() != rel:
        return False
    if rel.startswith("/") or rel.startswith("\\"):
        return False
    if "\\" in rel:
        return False
    parts = PurePosixPath(rel).parts
    if ".." in parts:
        return False
    if rel.startswith("~"):
        return False
    return True


def validate_relative_path(path: str, *, label: str = "path") -> str:
    if not isinstance(path, str) or not path:
        raise PathSafetyError(f"{label} must be a non-empty string")
    if not _is_safe_relative(path):
        raise PathSafetyError(f"unsafe {label}: {path!r}")
    return path


def resolve_under(base: Path, rel: str) -> Path:
    validate_relative_path(rel, label="path")
    base = base.resolve()
    target = (base / rel).resolve()
    if not str(target).startswith(str(base) + os.sep) and target != base:
        raise PathSafetyError(f"path escapes base: {rel!r}")
    return target


def assert_no_duplicate_paths(paths: list[str]) -> None:
    seen: set[str] = set()
    for p in paths:
        norm = PurePosixPath(p).as_posix()
        if norm in seen:
            raise PathSafetyError(f"duplicate output path: {p!r}")
        seen.add(norm)