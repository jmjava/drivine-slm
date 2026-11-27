from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PILOT_QUERY = REPO / "benchmarks" / "pilot" / "pilot-query-001"
PILOT_TIMEOUT = REPO / "benchmarks" / "pilot" / "pilot-timeout-001"


class TestDrivineRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import sys

        sys.path.insert(0, str(REPO / "python"))

    def test_schema_rejects_unknown_fields(self) -> None:
        from drivine_runner.schema import TaskSpecError, validate_task_dict

        data = json.loads((PILOT_QUERY / "task.json").read_text(encoding="utf-8"))
        data["extra_field"] = "nope"
        with self.assertRaises(TaskSpecError) as ctx:
            validate_task_dict(data, task_path=PILOT_QUERY / "task.json")
        self.assertIn("unknown task fields", str(ctx.exception))

    def test_project_symlink_outside_task_is_rejected(self) -> None:
        from drivine_runner.extract import ExtractionError, load_project_outputs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "proj"
            secret = root / "secret"
            project.mkdir()
            secret.mkdir()
            (secret / "answer.txt").write_text("secret\n", encoding="utf-8")
            os.symlink(secret / "answer.txt", project / "answer.txt")
            with self.assertRaises(ExtractionError):
                load_project_outputs(project, ("answer.txt",))

    def test_schema_rejects_path_traversal_outputs(self) -> None:
        from drivine_runner.schema import TaskSpecError, validate_task_dict

        data = json.loads((PILOT_QUERY / "task.json").read_text(encoding="utf-8"))
        data["expected_output_files"] = ["../escape.txt"]
        with self.assertRaises(TaskSpecError) as ctx:
            validate_task_dict(data, task_path=PILOT_QUERY / "task.json")
        self.assertIn("unsafe", str(ctx.exception))

    def test_known_good_passes(self) -> None:
        from drivine_runner.run import RunInput, run_task

        good = (PILOT_QUERY / "answers" / "good.md").read_text(encoding="utf-8")
        result = run_task(RunInput(task_path=PILOT_QUERY / "task.json", answer_text=good))
        self.assertTrue(result["full_task_success"])
        self.assertEqual(result["task_id"], "pilot-query-001")
        self.assertEqual(result["runner_version"], "0.1.0")
        self.assertIsNotNone(result["stdout_sha256"])
        self.assertEqual(result["stage"], "complete")

    def test_known_bad_fails(self) -> None:
        from drivine_runner.run import RunInput, run_task

        bad = (PILOT_QUERY / "answers" / "bad.md").read_text(encoding="utf-8")
        result = run_task(RunInput(task_path=PILOT_QUERY / "task.json", answer_text=bad))
        self.assertFalse(result["full_task_success"])
        self.assertFalse(result["passed"])

    def test_extraction_failure(self) -> None:
        from drivine_runner.run import RunInput, run_task

        result = run_task(
            RunInput(
                task_path=PILOT_QUERY / "task.json",
                answer_text="no fences here",
            )
        )
        self.assertFalse(result["full_task_success"])
        self.assertEqual(result["stage"], "extraction")

    def test_timeout(self) -> None:
        from unittest.mock import patch

        from drivine_runner.oracle import OracleResult
        from drivine_runner.run import RunInput, run_task

        answer = "```stub.txt\nok\n```"
        timed = OracleResult(
            exit_code=None,
            timed_out=True,
            stdout=b"",
            stderr=b"",
            transport_error=None,
        )
        with patch(
            "drivine_runner.run.run_oracle",
            return_value=timed,
        ) as mock_oracle:
            result = run_task(
                RunInput(task_path=PILOT_TIMEOUT / "task.json", answer_text=answer)
            )
            mock_oracle.assert_called_once()
        self.assertFalse(result["full_task_success"])
        self.assertTrue(result["oracle_timed_out"])
        self.assertEqual(result["failure_reason"], "oracle timed out")

    def test_result_fields_bounded_previews(self) -> None:
        from drivine_runner.constants import STDOUT_STDERR_PREVIEW_MAX
        from drivine_runner.run import RunInput, run_task

        good = (PILOT_QUERY / "answers" / "good.md").read_text(encoding="utf-8")
        result = run_task(RunInput(task_path=PILOT_QUERY / "task.json", answer_text=good))
        self.assertLessEqual(len(result["stdout_preview"]), STDOUT_STDERR_PREVIEW_MAX + 1)
        self.assertLessEqual(len(result["stderr_preview"]), STDOUT_STDERR_PREVIEW_MAX + 1)


if __name__ == "__main__":
    unittest.main()