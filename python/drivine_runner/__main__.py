from __future__ import annotations

import argparse
import sys
from pathlib import Path

from drivine_runner.run import RunInput, format_result_json, run_task
from drivine_runner.schema import TaskSpecError, load_task_spec


def _repo_pilot_dir() -> Path:
    # python/drivine_runner/__main__.py -> repo root
    return Path(__file__).resolve().parents[2] / "benchmarks" / "pilot"


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        spec = load_task_spec(Path(args.task))
    except TaskSpecError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 1
    print(f"ok: {spec.task_id} ({spec.area})")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    answer_text: str | None = None
    if args.answer is not None:
        answer_text = Path(args.answer).read_text(encoding="utf-8")
    project_dir = Path(args.project_dir) if args.project_dir else None
    result = run_task(
        RunInput(
            task_path=Path(args.task),
            answer_text=answer_text,
            project_dir=project_dir,
        )
    )
    sys.stdout.write(format_result_json(result))
    return 0 if result.get("full_task_success") else 1


def cmd_self_test(_: argparse.Namespace) -> int:
    pilot = _repo_pilot_dir() / "pilot-query-001"
    task = pilot / "task.json"
    good = (pilot / "answers" / "good.md").read_text(encoding="utf-8")
    bad = (pilot / "answers" / "bad.md").read_text(encoding="utf-8")

    good_result = run_task(RunInput(task_path=task, answer_text=good))
    bad_result = run_task(RunInput(task_path=task, answer_text=bad))

    failures: list[str] = []
    if not good_result.get("full_task_success"):
        failures.append(f"known-good failed: {good_result.get('failure_reason')}")
    if bad_result.get("full_task_success"):
        failures.append("known-bad unexpectedly passed")

    if failures:
        for line in failures:
            print(line, file=sys.stderr)
        return 1

    print("self-test ok: known-good passed, known-bad failed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m drivine_runner")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="validate a task spec JSON file")
    p_validate.add_argument("--task", required=True)
    p_validate.set_defaults(func=cmd_validate)

    p_run = sub.add_parser("run", help="score one model answer against a task")
    p_run.add_argument("--task", required=True)
    p_run.add_argument("--answer", default=None, help="markdown answer file")
    p_run.add_argument("--project-dir", default=None, help="directory with output files")
    p_run.set_defaults(func=cmd_run)

    p_self = sub.add_parser("self-test", help="run built-in pilot known-good/bad checks")
    p_self.set_defaults(func=cmd_self_test)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())