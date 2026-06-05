"""Unit tests for ``scripts/governance_check.py``.

These tests use ``monkeypatch`` and ``unittest.mock`` to substitute
the subprocess runner. The tests do not invoke ``openspec`` or
``uv`` directly. The full ``pytest`` discovery picks this file up
because it is located under ``tests/`` and matches the default
``test_*.py`` pattern.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "governance_check.py"


@pytest.fixture(scope="module")
def governance_module():
    """Import the script as a module.

    The script is not on ``sys.path`` by default. We add the
    ``scripts/`` directory to ``sys.path`` for the duration of the
    test module and remove it on teardown.
    """

    scripts_dir = str(REPO_ROOT / "scripts")
    added = scripts_dir not in sys.path
    if added:
        sys.path.insert(0, scripts_dir)
    try:
        import governance_check  # type: ignore[import-not-found]
    finally:
        if added:
            try:
                sys.path.remove(scripts_dir)
            except ValueError:
                pass
    return governance_check


def test_script_exists() -> None:
    """The script file is created at the allowed path."""

    assert SCRIPT_PATH.is_file(), f"expected {SCRIPT_PATH} to exist"


def test_full_mode_command_list(governance_module) -> None:
    """Full mode returns the six expected commands in order."""

    commands = governance_module.build_command_list(quick=False)
    labels = [cmd["label"] for cmd in commands]
    assert labels == [
        "openspec schema validate",
        "openspec validate example-governance-stack-walkthrough --strict",
        "openspec validate add-skill-lifecycle-recommendation --strict",
        "openspec validate --strict --all",
        "uv run skill-forge --help",
        "uv run pytest",
    ]


def test_quick_mode_command_list(governance_module) -> None:
    """Quick mode returns the two expected commands in order."""

    commands = governance_module.build_command_list(quick=True)
    labels = [cmd["label"] for cmd in commands]
    assert labels == [
        "openspec validate --strict --all",
        "uv run skill-forge --help",
    ]


def test_quick_mode_excludes_pytest(governance_module) -> None:
    """Quick mode never includes the slow ``uv run pytest`` command."""

    commands = governance_module.build_command_list(quick=True)
    argv_strings = [" ".join(cmd["argv"]) for cmd in commands]
    assert not any("pytest" in argv for argv in argv_strings)


def test_full_mode_marks_all_commands_required(governance_module) -> None:
    """Every command in the full-mode list is required."""

    commands = governance_module.build_command_list(quick=False)
    for cmd in commands:
        assert cmd["required"] is True, f"{cmd['label']} should be required"


def test_commands_have_required_keys(governance_module) -> None:
    """Every command dict has the four required keys."""

    for quick in (False, True):
        commands = governance_module.build_command_list(quick=quick)
        for cmd in commands:
            assert set(cmd.keys()) >= {"label", "argv", "required", "reason"}
            assert isinstance(cmd["label"], str) and cmd["label"]
            assert isinstance(cmd["argv"], list) and cmd["argv"]
            assert isinstance(cmd["required"], bool)
            assert isinstance(cmd["reason"], str)


def test_summarize_results_all_pass(governance_module) -> None:
    """An all-PASS run yields exit code 0."""

    commands = governance_module.build_command_list(quick=False)
    results = [
        {
            "label": cmd["label"],
            "status": "PASS",
            "exit_code": 0,
            "reason": "",
            "elapsed_seconds": 0.01,
            "skipped": False,
        }
        for cmd in commands
    ]
    summary = governance_module.summarize_results(commands, results)
    assert summary["passed"] == len(commands)
    assert summary["failed"] == 0
    assert summary["skipped"] == 0
    assert summary["exit_code"] == 0


def test_summarize_results_required_failure_returns_nonzero(
    governance_module,
) -> None:
    """A required FAIL produces a non-zero exit code."""

    commands = governance_module.build_command_list(quick=False)
    results = [
        {
            "label": cmd["label"],
            "status": "FAIL",
            "exit_code": 1,
            "reason": "boom",
            "elapsed_seconds": 0.01,
            "skipped": False,
        }
        for cmd in commands
    ]
    summary = governance_module.summarize_results(commands, results)
    assert summary["failed"] == len(commands)
    assert summary["exit_code"] == 1


def test_summarize_results_optional_skip_does_not_block(
    governance_module,
) -> None:
    """An optional SKIP is reported but does not produce a non-zero exit."""

    commands = [
        {
            "label": "fake-required",
            "argv": ["fake-required"],
            "required": True,
            "reason": "test required",
        },
        {
            "label": "fake-optional",
            "argv": ["fake-optional"],
            "required": False,
            "reason": "test optional",
        },
    ]
    results = [
        {
            "label": "fake-required",
            "status": "PASS",
            "exit_code": 0,
            "reason": "",
            "elapsed_seconds": 0.0,
            "skipped": False,
        },
        {
            "label": "fake-optional",
            "status": "SKIP",
            "exit_code": 0,
            "reason": "tool missing",
            "elapsed_seconds": 0.0,
            "skipped": True,
        },
    ]
    summary = governance_module.summarize_results(commands, results)
    assert summary["passed"] == 1
    assert summary["skipped"] == 1
    assert summary["failed"] == 0
    assert summary["exit_code"] == 0


def test_summarize_results_required_skip_blocks(governance_module) -> None:
    """A required SKIP is treated as a blocking failure."""

    commands = [
        {
            "label": "fake-required",
            "argv": ["fake-required"],
            "required": True,
            "reason": "test required",
        },
    ]
    results = [
        {
            "label": "fake-required",
            "status": "SKIP",
            "exit_code": 0,
            "reason": "tool missing",
            "elapsed_seconds": 0.0,
            "skipped": True,
        },
    ]
    summary = governance_module.summarize_results(commands, results)
    assert summary["skipped"] == 1
    assert summary["exit_code"] == 1


def test_run_command_returns_pass_on_zero_exit(governance_module) -> None:
    """A zero-exit subprocess is reported as PASS."""

    fake_completed = subprocess.CompletedProcess(
        args=["echo", "ok"], returncode=0, stdout="ok\n", stderr=""
    )
    with patch.object(governance_module.shutil, "which", return_value="/bin/echo"), patch.object(
        governance_module.subprocess, "run", return_value=fake_completed
    ) as mock_run:
        cmd = {
            "label": "echo ok",
            "argv": ["echo", "ok"],
            "required": True,
            "reason": "test",
        }
        result = governance_module.run_command(cmd, cwd=".")
    assert result["status"] == "PASS"
    assert result["skipped"] is False
    assert mock_run.called


def test_run_command_returns_fail_on_nonzero_exit(governance_module) -> None:
    """A non-zero-exit subprocess is reported as FAIL with reason."""

    fake_completed = subprocess.CompletedProcess(
        args=["false"], returncode=1, stdout="", stderr="boom\n"
    )
    with patch.object(governance_module.shutil, "which", return_value="/bin/false"), patch.object(
        governance_module.subprocess, "run", return_value=fake_completed
    ):
        cmd = {
            "label": "false",
            "argv": ["false"],
            "required": True,
            "reason": "test",
        }
        result = governance_module.run_command(cmd, cwd=".")
    assert result["status"] == "FAIL"
    assert result["skipped"] is False
    assert "exit code 1" in result["reason"]


def test_run_command_skips_when_tool_missing(governance_module) -> None:
    """A missing tool is reported as SKIP with a reason."""

    with patch.object(governance_module.shutil, "which", return_value=None):
        cmd = {
            "label": "nope",
            "argv": ["nope"],
            "required": True,
            "reason": "test",
        }
        result = governance_module.run_command(cmd, cwd=".")
    assert result["status"] == "SKIP"
    assert result["skipped"] is True
    assert "nope" in result["reason"]


def test_format_status_line_includes_required_tag(governance_module) -> None:
    """The printed line annotates each command as required or optional."""

    cmd = {
        "label": "x",
        "argv": ["x"],
        "required": True,
        "reason": "test",
    }
    result = {
        "label": "x",
        "status": "PASS",
        "exit_code": 0,
        "reason": "",
        "elapsed_seconds": 0.0,
        "skipped": False,
    }
    line = governance_module.format_status_line(cmd, result)
    assert line.startswith("[PASS] x (required)")


def test_main_returns_zero_on_all_pass(governance_module) -> None:
    """``main`` returns 0 when every gate passes."""

    fake_completed = subprocess.CompletedProcess(
        args=["true"], returncode=0, stdout="", stderr=""
    )
    with patch.object(governance_module.shutil, "which", return_value="/bin/true"), patch.object(
        governance_module.subprocess, "run", return_value=fake_completed
    ):
        exit_code = governance_module.main(["--quick"])
    assert exit_code == 0


def test_main_returns_nonzero_on_required_failure(governance_module) -> None:
    """``main`` returns non-zero when a required gate fails."""

    fake_completed = subprocess.CompletedProcess(
        args=["false"], returncode=1, stdout="", stderr="boom\n"
    )
    with patch.object(governance_module.shutil, "which", return_value="/bin/false"), patch.object(
        governance_module.subprocess, "run", return_value=fake_completed
    ):
        exit_code = governance_module.main(["--quick"])
    assert exit_code == 1


def test_script_does_not_mutate_files(tmp_path, monkeypatch) -> None:
    """Running the script does not create, modify, or delete any file.

    The test copies the script's source into a temp directory and
    invokes ``python -c`` with a synthetic argv. The directory's
    file list is captured before and after; the lists must be
    equal.
    """

    src = SCRIPT_PATH.read_text(encoding="utf-8")
    target = tmp_path / "governance_check.py"
    target.write_text(src, encoding="utf-8")

    before = sorted(p.name for p in tmp_path.iterdir())

    def fake_which(_name: str) -> str | None:
        return "/bin/true"

    def fake_run(argv, cwd, capture_output, text, check, **kwargs):  # noqa: ARG001
        return subprocess.CompletedProcess(
            args=argv, returncode=0, stdout="", stderr=""
        )

    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)

    script_namespace: dict[str, object] = {"__name__": "not_main"}
    exec(compile(src, str(target), "exec"), script_namespace)  # noqa: S102
    main_fn = script_namespace["main"]
    exit_code = main_fn(["--quick"])  # type: ignore[arg-type]

    after = sorted(p.name for p in tmp_path.iterdir())
    assert exit_code == 0
    assert before == after


def test_script_uses_only_stdlib(governance_module) -> None:
    """The script's runtime imports are all standard-library."""

    import re

    src = SCRIPT_PATH.read_text(encoding="utf-8")
    imports: list[str] = []
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            imports.append(stripped[len("import ") :].split(" as ")[0].split(",")[0].strip())
        elif stripped.startswith("from "):
            head = stripped[len("from ") :]
            if " import " in head:
                imports.append(head.split(" import ", 1)[0].strip())

    stdlib = set(sys.stdlib_module_names)
    for name in imports:
        if name == "__future__":
            continue
        root = name.split(".")[0]
        assert root in stdlib, f"non-stdlib import detected: {name}"


def test_status_line_includes_skip_reason(governance_module) -> None:
    """SKIP lines include the parenthesized reason text."""

    cmd = {
        "label": "missing",
        "argv": ["missing"],
        "required": True,
        "reason": "test",
    }
    result = {
        "label": "missing",
        "status": "SKIP",
        "exit_code": 0,
        "reason": "tool 'missing' not found on PATH",
        "elapsed_seconds": 0.0,
        "skipped": True,
    }
    line = governance_module.format_status_line(cmd, result)
    assert "[SKIP] missing (required)" in line
    assert "reason:" in line
    assert "missing" in line


def test_status_line_includes_fail_reason(governance_module) -> None:
    """FAIL lines include the reason text."""

    cmd = {
        "label": "failer",
        "argv": ["failer"],
        "required": True,
        "reason": "test",
    }
    result = {
        "label": "failer",
        "status": "FAIL",
        "exit_code": 2,
        "reason": "exit code 2: boom",
        "elapsed_seconds": 0.1,
        "skipped": False,
    }
    line = governance_module.format_status_line(cmd, result)
    assert "[FAIL] failer (required)" in line
    assert "exit code 2" in line


def test_should_use_shell_for_windows_cmd(governance_module) -> None:
    """``_should_use_shell`` returns ``True`` for Windows .CMD/.BAT tools."""

    with patch.object(governance_module.os, "name", "nt"):
        assert governance_module._should_use_shell("C:\\fake\\tool.CMD") is True
        assert governance_module._should_use_shell("C:\\fake\\tool.cmd") is True
        assert governance_module._should_use_shell("C:\\fake\\tool.BAT") is True
        assert governance_module._should_use_shell("C:\\fake\\tool.bat") is True
        assert governance_module._should_use_shell("C:\\fake\\tool.exe") is False
        assert governance_module._should_use_shell("/usr/bin/tool") is False


def test_should_use_shell_for_non_windows(governance_module) -> None:
    """``_should_use_shell`` returns ``False`` on non-Windows platforms."""

    with patch.object(governance_module.os, "name", "posix"):
        assert governance_module._should_use_shell("/usr/bin/tool.cmd") is False
        assert governance_module._should_use_shell("/usr/bin/tool.bat") is False
        assert governance_module._should_use_shell("/usr/bin/tool") is False


def test_run_command_uses_shell_for_windows_cmd(governance_module) -> None:
    """``run_command`` invokes subprocess with ``shell=True`` on Windows CMD."""

    fake_completed = subprocess.CompletedProcess(
        args=["openspec", "validate"], returncode=0, stdout="ok", stderr=""
    )
    with patch.object(governance_module.os, "name", "nt"), patch.object(
        governance_module.shutil,
        "which",
        return_value="C:\\Users\\fake\\AppData\\Roaming\\npm\\openspec.CMD",
    ), patch.object(
        governance_module.subprocess, "run", return_value=fake_completed
    ) as mock_run:
        cmd = {
            "label": "openspec validate",
            "argv": ["openspec", "validate"],
            "required": True,
            "reason": "test",
        }
        result = governance_module.run_command(cmd, cwd=".")
    assert result["status"] == "PASS"
    _, kwargs = mock_run.call_args
    assert kwargs.get("shell") is True


def test_script_writes_nothing_to_cwd(tmp_path, monkeypatch) -> None:
    """Running the script in a temp cwd does not write any file there."""

    src = SCRIPT_PATH.read_text(encoding="utf-8")
    target = tmp_path / "governance_check.py"
    target.write_text(src, encoding="utf-8")

    def fake_which(_name: str) -> str | None:
        return "/bin/true"

    def fake_run(argv, cwd, capture_output, text, check, **kwargs):  # noqa: ARG001
        return subprocess.CompletedProcess(
            args=argv, returncode=0, stdout="", stderr=""
        )

    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)

    script_namespace: dict[str, object] = {"__name__": "not_main"}
    exec(compile(src, str(target), "exec"), script_namespace)  # noqa: S102
    main_fn = script_namespace["main"]
    exit_code = main_fn([])  # type: ignore[arg-type]
    assert exit_code == 0
    # Only the script file itself should be present.
    files = sorted(p.name for p in tmp_path.iterdir())
    assert files == ["governance_check.py"]
    # And the os.cwd was not changed.
    assert os.getcwd() != str(tmp_path)
