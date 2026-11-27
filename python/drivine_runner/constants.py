from __future__ import annotations

TASK_SPEC_VERSION = "1"
RUNNER_VERSION = "0.1.0"

DRIVINE_DOMAIN = "drivine"

REGISTERED_DRIVINE_AREAS = frozenset(
    {"generation", "repair", "query", "graph_rag", "integration"}
)

REQUIRED_TASK_KEYS = frozenset(
    {
        "task_spec_version",
        "task_id",
        "domain",
        "area",
        "prompt",
        "answer_language",
        "expected_output_files",
        "fixture_dir",
        "oracle_argv",
        "timeout_seconds",
        "pins",
        "checks",
    }
)

ORACLE_ENV_ALLOWLIST = frozenset(
    {
        "PATH",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "PYTHONIOENCODING",
        "TMPDIR",
        "TEMP",
        "TMP",
    }
)

STDOUT_STDERR_PREVIEW_MAX = 400