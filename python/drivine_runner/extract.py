from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from drivine_runner.paths import PathSafetyError, resolve_under, validate_relative_path

FENCE_RE = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)

PATH_LABEL_PREFIXES = (
    "python ",
    "text ",
    "plaintext ",
    "json ",
    "typescript ",
    "javascript ",
    "python:",
    "text:",
    "plaintext:",
    "json:",
)


@dataclass(frozen=True)
class ExtractedFile:
    path: str
    content: str


class ExtractionError(ValueError):
    pass


def _normalize_fence_label(label: str) -> str:
    label = label.strip()
    lower = label.lower()
    for prefix in PATH_LABEL_PREFIXES:
        if lower.startswith(prefix):
            label = label[len(prefix) :].strip()
            break
    if label.lower().startswith("file:"):
        label = label[5:].strip()
    if label.lower().startswith("path:"):
        label = label[5:].strip()
    label = label.lstrip("./")
    if not label:
        raise ExtractionError("fenced block missing explicit file path in label")
    validate_relative_path(label, label="fence path")
    return label


def extract_fenced_files(text: str) -> list[ExtractedFile]:
    if not text or not text.strip():
        raise ExtractionError("empty answer text")
    found: list[ExtractedFile] = []
    for match in FENCE_RE.finditer(text):
        label, body = match.group(1), match.group(2)
        if not body.strip():
            continue
        try:
            path = _normalize_fence_label(label)
        except PathSafetyError as exc:
            raise ExtractionError(str(exc)) from exc
        content = body.rstrip("\n") + "\n"
        found.append(ExtractedFile(path=path, content=content))
    if not found:
        raise ExtractionError("no fenced code blocks with explicit file paths found")
    return found


def filter_declared_outputs(
    extracted: list[ExtractedFile], declared: tuple[str, ...]
) -> dict[str, str]:
    declared_set = set(declared)
    out: dict[str, str] = {}
    for item in extracted:
        if item.path not in declared_set:
            raise ExtractionError(
                f"extracted undeclared output file {item.path!r}; "
                f"allowed: {sorted(declared_set)}"
            )
        if item.path in out:
            raise ExtractionError(f"duplicate extracted path {item.path!r}")
        out[item.path] = item.content
    missing = declared_set - set(out)
    if missing:
        raise ExtractionError(f"missing declared output files: {sorted(missing)}")
    return out


def load_project_outputs(project_dir: Path, declared: tuple[str, ...]) -> dict[str, str]:
    project_dir = project_dir.resolve()
    if not project_dir.is_dir():
        raise ExtractionError(f"project directory not found: {project_dir}")
    out: dict[str, str] = {}
    for rel in declared:
        src = project_dir / rel
        if not src.is_file():
            raise ExtractionError(f"project missing declared file: {rel}")
        try:
            validate_relative_path(rel)
        except PathSafetyError as exc:
            raise ExtractionError(str(exc)) from exc
        try:
            resolved = resolve_under(project_dir, rel)
        except PathSafetyError as exc:
            raise ExtractionError(str(exc)) from exc
        if resolved.is_symlink() or not resolved.is_file():
            raise ExtractionError(f"project path escapes root: {rel}")
        out[rel] = resolved.read_text(encoding="utf-8")
    return out


def copy_fixture_tree(fixture_root: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for src in sorted(fixture_root.rglob("*")):
        rel = src.relative_to(fixture_root)
        if ".." in rel.parts:
            raise ExtractionError("fixture tree contains path traversal")
        target = dest / rel
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)