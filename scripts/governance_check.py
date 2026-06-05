#!/usr/bin/env python3
"""Lightweight local governance check for the Skill Forge repository.

The script runs the project's known governance gates in sequence and
prints a stable ``[PASS]``, ``[FAIL]``, or ``[SKIP]`` line per
command. It uses only the Python standard library and never modifies
files in the working directory.

Usage:

    python scripts/governance_check.py            # full mode (default)
    python scripts/governance_check.py --quick    # quick mode (subset)

Exit code:

    0  every required command passed (skipped optional is allowed)
    1  any required command failed, or any required command was
       skipped because the underlying tool is missing
    2  invalid arguments

The script is intentionally read-only. It is a reporter, not a
writer. See ``openspec/changes/add-governance-enforcement-hooks/``
for the design and ``docs/00-project/governance-enforcement-verification-report.md``
for the latest recorded run.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from typing import Any


def _should_use_shell(tool_path: str) -> bool:
    """Return whether ``subprocess.run`` should use ``shell=True`` for a tool.

    On Windows, ``subprocess.run`` cannot directly execute a ``.CMD``
    or ``.BAT`` file when ``shell=False``; the call raises a
    ``FileNotFoundError`` even when the file exists. The fix is to
    invoke the command through the user's shell. On non-Windows
    platforms the function always returns ``False``.
    """

    if os.name != "nt":
        return False
    lowered = tool_path.lower()
    return lowered.endswith(".cmd") or lowered.endswith(".bat")


FULL_COMMANDS = [
    {
        "label": "openspec schema validate",
        "argv": ["openspec", "schema", "validate"],
        "required": True,
        "reason": "validates the OpenSpec schema structure",
    },
    {
        "label": "openspec validate example-governance-stack-walkthrough --strict",
        "argv": [
            "openspec",
            "validate",
            "example-governance-stack-walkthrough",
            "--strict",
        ],
        "required": True,
        "reason": "validates the example governance change",
    },
    {
        "label": "openspec validate add-skill-lifecycle-recommendation --strict",
        "argv": [
            "openspec",
            "validate",
            "add-skill-lifecycle-recommendation",
            "--strict",
        ],
        "required": True,
        "reason": "validates the Phase 3 governance change",
    },
    {
        "label": "openspec validate --strict --all",
        "argv": ["openspec", "validate", "--strict", "--all"],
        "required": True,
        "reason": "validates every change and spec",
    },
    {
        "label": "uv run skill-forge --help",
        "argv": ["uv", "run", "skill-forge", "--help"],
        "required": True,
        "reason": "smoke test the CLI entry point",
    },
    {
        "label": "uv run pytest",
        "argv": ["uv", "run", "pytest"],
        "required": True,
        "reason": "runs the full test suite",
    },
]


QUICK_COMMANDS = [
    {
        "label": "openspec validate --strict --all",
        "argv": ["openspec", "validate", "--strict", "--all"],
        "required": True,
        "reason": "validates every change and spec",
    },
    {
        "label": "uv run skill-forge --help",
        "argv": ["uv", "run", "skill-forge", "--help"],
        "required": True,
        "reason": "smoke test the CLI entry point",
    },
]


def build_command_list(quick: bool) -> list[dict[str, Any]]:
    """Return the command list for the requested mode.

    Parameters
    ----------
    quick
        When ``True``, return the two-command quick list. When
        ``False``, return the six-command full list.

    Returns
    -------
    list[dict]
        A list of command dicts, each with ``label``, ``argv``,
        ``required``, and ``reason`` keys. The order is the
        order in which the script runs the commands.
    """

    if quick:
        return [dict(cmd) for cmd in QUICK_COMMANDS]
    return [dict(cmd) for cmd in FULL_COMMANDS]


def run_command(cmd: dict[str, Any], cwd: str) -> dict[str, Any]:
    """Run a single command and return a result dict.

    The function does not raise on a non-zero exit code; it
    captures the exit code and returns a result dict so the
    caller can aggregate results. The function uses
    :func:`shutil.which` to detect a missing tool before
    invoking :func:`subprocess.run`. A missing required tool
    is reported as ``SKIP`` with a parenthesized reason.

    Parameters
    ----------
    cmd
        A command dict as returned by
        :func:`build_command_list`.
    cwd
        The working directory in which to run the command.

    Returns
    -------
    dict
        A result dict with ``label``, ``status``, ``exit_code``,
        ``reason``, ``elapsed_seconds``, and ``skipped`` keys.
    """

    executable = cmd["argv"][0]
    tool_path = shutil.which(executable)
    if tool_path is None:
        return {
            "label": cmd["label"],
            "status": "SKIP",
            "exit_code": 0,
            "reason": f"tool '{executable}' not found on PATH",
            "elapsed_seconds": 0.0,
            "skipped": True,
        }

    use_shell = _should_use_shell(tool_path)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            cmd["argv"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            shell=use_shell,
        )
    except FileNotFoundError as exc:
        elapsed = time.monotonic() - started
        return {
            "label": cmd["label"],
            "status": "SKIP",
            "exit_code": 0,
            "reason": f"tool '{executable}' not found on PATH ({exc})",
            "elapsed_seconds": elapsed,
            "skipped": True,
        }
    except OSError as exc:
        elapsed = time.monotonic() - started
        return {
            "label": cmd["label"],
            "status": "FAIL",
            "exit_code": 1,
            "reason": f"OS error while running '{executable}': {exc}",
            "elapsed_seconds": elapsed,
            "skipped": False,
        }

    elapsed = time.monotonic() - started
    if completed.returncode == 0:
        return {
            "label": cmd["label"],
            "status": "PASS",
            "exit_code": 0,
            "reason": "",
            "elapsed_seconds": elapsed,
            "skipped": False,
        }

    detail = (completed.stderr or completed.stdout or "").strip().splitlines()
    snippet = detail[-1] if detail else ""
    reason = f"exit code {completed.returncode}"
    if snippet:
        reason = f"{reason}: {snippet[:200]}"
    return {
        "label": cmd["label"],
        "status": "FAIL",
        "exit_code": completed.returncode,
        "reason": reason,
        "elapsed_seconds": elapsed,
        "skipped": False,
    }


def summarize_results(
    commands: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate per-command results into a single summary.

    The function returns a dict with ``passed``, ``failed``,
    ``skipped``, ``exit_code``, and ``per_command`` keys.

    Parameters
    ----------
    commands
        The command list that produced the results. The
        ``required`` flag is read from this list, not from
        ``results``, so a future change can extend the
        per-command metadata without breaking the aggregator.
    results
        The result list, in the same order as ``commands``.

    Returns
    -------
    dict
        A summary dict. ``exit_code`` is ``1`` when any
        required command failed or any required command was
        skipped because the underlying tool is missing.
    """

    passed = 0
    failed = 0
    skipped = 0
    blocking_failure = False
    per_command: list[dict[str, Any]] = []

    for cmd, result in zip(commands, results):
        per_command.append({"command": cmd, "result": result})
        if result["status"] == "PASS":
            passed += 1
        elif result["status"] == "SKIP":
            skipped += 1
            if cmd.get("required", True):
                blocking_failure = True
        else:
            failed += 1
            if cmd.get("required", True):
                blocking_failure = True

    exit_code = 1 if blocking_failure else 0
    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "exit_code": exit_code,
        "per_command": per_command,
    }


def format_status_line(cmd: dict[str, Any], result: dict[str, Any]) -> str:
    """Format a single ``[STATUS] label`` line for printing.

    Parameters
    ----------
    cmd
        The command dict, used to look up the ``required`` flag
        so the printed line can include a ``(required)`` or
        ``(optional)`` annotation.
    result
        The result dict returned by :func:`run_command`.

    Returns
    -------
    str
        The formatted line, without a trailing newline.
    """

    required_tag = "required" if cmd.get("required", True) else "optional"
    base = f"[{result['status']}] {result['label']} ({required_tag})"
    if result["status"] == "FAIL" and result["reason"]:
        return f"{base} -- {result['reason']}"
    if result["status"] == "SKIP" and result["reason"]:
        return f"{base} -- reason: {result['reason']}"
    return base


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the gate suite, and return the exit code.

    Parameters
    ----------
    argv
        Optional argument list. When ``None``, the function
        reads from :data:`sys.argv`. The function never raises
        on a gate failure; it returns a non-zero exit code
        instead.

    Returns
    -------
    int
        ``0`` when every required gate passed; ``1`` otherwise.
    """

    parser = argparse.ArgumentParser(
        prog="governance_check",
        description=(
            "Run the Skill Forge local governance gates. "
            "The script is read-only and uses only the Python "
            "standard library. Run from the repository root."
        ),
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="run only the two fast gates (skip pytest)",
    )
    args = parser.parse_args(argv)

    commands = build_command_list(quick=args.quick)
    cwd = "."
    results = [run_command(cmd, cwd=cwd) for cmd in commands]

    for cmd, result in zip(commands, results):
        print(format_status_line(cmd, result))

    summary = summarize_results(commands, results)
    print(
        "Summary: "
        f"{summary['passed']} passed, "
        f"{summary['failed']} failed, "
        f"{summary['skipped']} skipped"
    )
    return summary["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
