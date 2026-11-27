from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass

from drivine_runner.constants import ORACLE_ENV_ALLOWLIST, STDOUT_STDERR_PREVIEW_MAX


@dataclass(frozen=True)
class OracleResult:
    exit_code: int | None
    timed_out: bool
    stdout: bytes
    stderr: bytes
    transport_error: str | None

    @property
    def stdout_preview(self) -> str:
        return _preview(self.stdout)

    @property
    def stderr_preview(self) -> str:
        return _preview(self.stderr)

    @property
    def stdout_sha256(self) -> str:
        return hashlib.sha256(self.stdout).hexdigest()

    @property
    def stderr_sha256(self) -> str:
        return hashlib.sha256(self.stderr).hexdigest()


def _preview(data: bytes) -> str:
    text = data.decode("utf-8", errors="replace")
    if len(text) <= STDOUT_STDERR_PREVIEW_MAX:
        return text
    return text[: STDOUT_STDERR_PREVIEW_MAX] + "…"


def build_oracle_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for key in ORACLE_ENV_ALLOWLIST:
        val = os.environ.get(key)
        if val is not None:
            env[key] = val
    if "PATH" not in env:
        env["PATH"] = os.defpath
    return env


def run_oracle(argv: tuple[str, ...], *, cwd: str, timeout_seconds: float) -> OracleResult:
    try:
        proc = subprocess.run(
            list(argv),
            cwd=cwd,
            env=build_oracle_env(),
            shell=False,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return OracleResult(
            exit_code=proc.returncode,
            timed_out=False,
            stdout=proc.stdout or b"",
            stderr=proc.stderr or b"",
            transport_error=None,
        )
    except subprocess.TimeoutExpired as exc:
        return OracleResult(
            exit_code=None,
            timed_out=True,
            stdout=exc.stdout or b"" if exc.stdout else b"",
            stderr=exc.stderr or b"" if exc.stderr else b"",
            transport_error=None,
        )
    except PermissionError as exc:
        # Some sandboxes deny SIGKILL after a timeout; still report a timeout.
        return OracleResult(
            exit_code=None,
            timed_out=True,
            stdout=b"",
            stderr=b"",
            transport_error=str(exc),
        )
    except OSError as exc:
        return OracleResult(
            exit_code=None,
            timed_out=False,
            stdout=b"",
            stderr=b"",
            transport_error=str(exc),
        )