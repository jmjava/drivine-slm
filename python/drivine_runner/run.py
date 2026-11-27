from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from drivine_runner.constants import RUNNER_VERSION
from drivine_runner.extract import (
    ExtractionError,
    copy_fixture_tree,
    extract_fenced_files,
    filter_declared_outputs,
    load_project_outputs,
)
from drivine_runner.oracle import run_oracle
from drivine_runner.schema import FileCheck, TaskSpec, TaskSpecError, load_task_spec


@dataclass(frozen=True)
class RunInput:
    task_path: Path
    answer_text: str | None = None
    project_dir: Path | None = None


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_file_checks(project_root: Path, checks: tuple[FileCheck, ...]) -> tuple[bool, str | None]:
    for check in checks:
        target = project_root / check.path
        if not target.is_file():
            return False, f"check file missing: {check.path}"
        content = target.read_text(encoding="utf-8")
        if check.type == "file_equals":
            if content != check.expected_content:
                return False, f"file_equals mismatch: {check.path}"
        elif check.type == "file_sha256":
            digest = _sha256_text(content)
            if digest != check.expected_sha256:
                return False, f"file_sha256 mismatch: {check.path}"
        else:
            return False, f"unknown check type: {check.type}"
    return True, None


def _base_result(task: TaskSpec) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "passed": False,
        "full_task_success": False,
        "stage": "init",
        "runner_version": RUNNER_VERSION,
        "pins": {
            "source": task.pins.source,
            "package": task.pins.package,
        },
        "oracle_exit_code": None,
        "oracle_timed_out": False,
        "transport_error": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_preview": "",
        "stderr_preview": "",
        "failure_reason": None,
    }


def run_task(run_input: RunInput) -> dict[str, Any]:
    try:
        task = load_task_spec(run_input.task_path)
    except TaskSpecError as exc:
        return {
            "task_id": run_input.task_path.stem,
            "passed": False,
            "full_task_success": False,
            "stage": "task_validation",
            "runner_version": RUNNER_VERSION,
            "pins": None,
            "oracle_exit_code": None,
            "oracle_timed_out": False,
            "transport_error": None,
            "stdout_sha256": None,
            "stderr_sha256": None,
            "stdout_preview": "",
            "stderr_preview": "",
            "failure_reason": str(exc),
        }

    result = _base_result(task)
    if run_input.answer_text is not None and run_input.project_dir is not None:
        result.update(
            {
                "stage": "input",
                "failure_reason": "specify answer_text or project_dir, not both",
            }
        )
        return result
    if run_input.answer_text is None and run_input.project_dir is None:
        result.update(
            {
                "stage": "input",
                "failure_reason": "missing answer_text or project_dir",
            }
        )
        return result

    try:
        if run_input.project_dir is not None:
            outputs = load_project_outputs(
                run_input.project_dir, task.expected_output_files
            )
            result["stage"] = "extraction_project"
        else:
            extracted = extract_fenced_files(run_input.answer_text or "")
            outputs = filter_declared_outputs(extracted, task.expected_output_files)
            result["stage"] = "extraction_markdown"
    except ExtractionError as exc:
        result.update({"stage": "extraction", "failure_reason": str(exc)})
        return result

    try:
        with tempfile.TemporaryDirectory(prefix="drivine_runner_") as tmp:
            project = Path(tmp)
            copy_fixture_tree(task.fixture_path, project)
            for rel, content in outputs.items():
                dest = project / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")

            oracle = run_oracle(
                task.oracle_argv,
                cwd=str(project),
                timeout_seconds=task.timeout_seconds,
            )
            result["stage"] = "oracle"
            result["oracle_exit_code"] = oracle.exit_code
            result["oracle_timed_out"] = oracle.timed_out
            result["transport_error"] = oracle.transport_error
            result["stdout_sha256"] = oracle.stdout_sha256
            result["stderr_sha256"] = oracle.stderr_sha256
            result["stdout_preview"] = oracle.stdout_preview
            result["stderr_preview"] = oracle.stderr_preview

            if oracle.transport_error:
                result["failure_reason"] = oracle.transport_error
                return result
            if oracle.timed_out:
                result["failure_reason"] = "oracle timed out"
                return result
            if oracle.exit_code != 0:
                result["failure_reason"] = f"oracle exit code {oracle.exit_code}"
                return result

            ok, reason = _run_file_checks(project, task.checks)
            result["stage"] = "checks"
            if not ok:
                result["failure_reason"] = reason
                return result

    except Exception as exc:  # noqa: BLE001 — surfaced as transport error
        result.update(
            {
                "stage": "runner",
                "transport_error": str(exc),
                "failure_reason": str(exc),
            }
        )
        return result

    result["passed"] = True
    result["full_task_success"] = True
    result["stage"] = "complete"
    result["failure_reason"] = None
    return result


def format_result_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"