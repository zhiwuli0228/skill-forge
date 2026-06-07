"""Subprocess runner that captures 3 snapshots per run.

Each run produces exactly three snapshots in non-decreasing
timestamp order:
  1. start            (event: scenario_started)
  2. execution_complete (event: test_execution_finished)
  3. end              (event: results_parsed)

The runner is stdlib-only. It calls ``uv run pytest`` and
parses the pytest output to extract test counts. It is
deliberately decoupled from ``src/skill_forge/`` to match
the 001 harness posture.
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from ._types import RunRecord, RunSpec, Snapshot


_PYTEST_RESULT_RE = re.compile(
    r"=+\s*(?P<passed>\d+)\s+passed|\b(?P<failed>\d+)\s+failed|\b(?P<error>\d+)\s+error|\b(?P<skipped>\d+)\s+skipped"
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_run_id(profile: str, index: int) -> str:
    suffix = f"{int(time.time() * 1000) & 0xFFFFFFFF:08x}"
    return f"{profile.lower()}-run-{index:03d}-{suffix}"


def _parse_pytest_output(stdout: str) -> dict[str, int]:
    """Extract passed/failed/error/skipped counts from pytest's summary line.

    Returns a dict with zeroed keys if no summary is found.
    """
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total": 0}
    for line in stdout.splitlines():
        if "passed" not in line and "failed" not in line and "error" not in line:
            continue
        if "===" not in line and "no tests ran" not in line:
            continue
        for match in _PYTEST_RESULT_RE.finditer(line):
            for key in ("passed", "failed", "error", "skipped"):
                v = match.group(key)
                if v is not None:
                    counts[key if key != "error" else "errors"] += int(v)
        if "passed" in line or "failed" in line or "error" in line:
            break
    counts["total"] = counts["passed"] + counts["failed"] + counts["errors"] + counts["skipped"]
    return counts


def execute_run(
    run_spec: RunSpec,
    profile_name: str,
    run_index: int,
    project_root: Path,
    timeout_per_run: float = 600.0,
    extra_pytest_args: tuple[str, ...] = (),
) -> RunRecord:
    """Execute one ``uv run pytest`` invocation and capture 3 snapshots.

    Args:
        run_spec: Which files, seed, and base work units.
        profile_name: "STEADY" | "RAMP" | "BURST".
        run_index: 0-based index of this run within the profile.
        project_root: Working directory for the pytest invocation.
        timeout_per_run: Seconds before the subprocess is killed.
        extra_pytest_args: Additional args appended to the pytest command
            (e.g., ``("-k", "fast")`` for filtering).

    Returns:
        A ``RunRecord`` with exactly 3 snapshots in non-decreasing
        timestamp order.
    """
    run_id = _make_run_id(profile_name, run_index)
    test_files = list(run_spec.test_files)
    cmd = [
        "uv",
        "run",
        "pytest",
        *test_files,
        "-v",
        "--tb=line",
        "--no-header",
        *extra_pytest_args,
    ]

    start_iso = _now_iso()
    t0 = time.monotonic()

    snapshot_start = Snapshot(
        run_id=run_id,
        snapshot_index=0,
        phase="start",
        timestamp=start_iso,
        event="scenario_started",
        fields={"testFiles": test_files, "testFileCount": len(test_files)},
    )

    try:
        completed = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout_per_run,
        )
        exit_code = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        exit_code = -1
        stdout = (exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    except FileNotFoundError as exc:
        exit_code = -1
        stdout = ""
        stderr = f"subprocess failed: {exc}"

    duration_ms = (time.monotonic() - t0) * 1000.0
    end_iso = _now_iso()
    stdout_lines = stdout.count("\n")
    stderr_lines = stderr.count("\n")

    snapshot_exec = Snapshot(
        run_id=run_id,
        snapshot_index=1,
        phase="execution_complete",
        timestamp=end_iso,
        event="test_execution_finished",
        fields={
            "exitCode": exit_code,
            "durationMs": duration_ms,
            "stdoutLineCount": stdout_lines,
            "stderrLineCount": stderr_lines,
        },
    )

    test_results = _parse_pytest_output(stdout) if exit_code == 0 else {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "total": 0,
    }

    snapshot_end = Snapshot(
        run_id=run_id,
        snapshot_index=2,
        phase="end",
        timestamp=end_iso,
        event="results_parsed",
        fields={
            "testsPassed": test_results["passed"],
            "testsFailed": test_results["failed"],
            "testsError": test_results["errors"],
            "testsSkipped": test_results["skipped"],
            "totalTests": test_results["total"],
            "scenarioDurationMs": duration_ms,
        },
    )

    return RunRecord(
        run_id=run_id,
        scenario_profile=profile_name,
        seed=run_spec.seed,
        step_count=len(test_files),
        base_work_units=run_spec.base_work_units,
        baseline_policy_id="default-pytest",
        core_pool_size=1,
        maximum_pool_size=1,
        queue_capacity=len(test_files),
        command_line=" ".join(cmd),
        start_time=start_iso,
        end_time=end_iso,
        duration_ms=duration_ms,
        exit_code=exit_code,
        test_files=test_files,
        test_results=test_results,
        snapshots=[snapshot_start, snapshot_exec, snapshot_end],
    )


def run_profile(
    profile_name: str,
    specs: list[RunSpec],
    project_root: Path,
    timeout_per_run: float = 600.0,
    extra_pytest_args: tuple[str, ...] = (),
) -> list[RunRecord]:
    """Execute all RunSpecs in a profile, returning their RunRecords."""
    records: list[RunRecord] = []
    for i, spec in enumerate(specs):
        rec = execute_run(
            run_spec=spec,
            profile_name=profile_name,
            run_index=i,
            project_root=project_root,
            timeout_per_run=timeout_per_run,
            extra_pytest_args=extra_pytest_args,
        )
        records.append(rec)
    return records
