# Verification Policy

## Purpose

This document defines the minimum verification required for every change type in the Skill Forge repository, the required use of `scripts/governance_check.py`, and how to record skipped or failed verification.

## Scope

- Applies to: every change in the Skill Forge repository.
- Owns: the per-change-type verification floor, the gate (`scripts/governance_check.py`), and the recording format for skipped or failed verification.
- Does **not** own: per-flow verification mechanics (see `docs/01-architecture/data-flow.md`) or per-agent workflow (see `agent-workflow.md`).

## Current Rules

### 1. Verification Is Mandatory

No agent may declare a task complete without verification evidence. Evidence must include:

- The exact verification commands run.
- The exit status of each command.
- For diff-producing commands, the list of changed files.
- For test commands, the pass/fail count or a clear "skipped" reason.

If a verification command cannot run, the agent must record the command as written, the reason it could not run (environment, missing tool, blocked dependency), and whether the failure is blocking for the current phase. "Looks good" is not verification. "It compiled" is not verification for tasks that require tests.

### 2. Verification Floor by Change Type

The minimum verification is **the gate plus the per-flow checks the change touches**.

| Change type | Minimum verification |
|---|---|
| Docs-only change (markdown only, no code, no spec) | `python scripts/governance_check.py --quick` |
| Schema or governance change (OpenSpec, SuperSpec, harness rules) | `python scripts/governance_check.py` (full mode) |
| Code change that touches a runtime module under `src/skill_forge/` | `python scripts/governance_check.py` plus the targeted tests for the touched module(s) plus `uv run skill-forge --help` |
| Code change that alters CLI output, stored artifact format, or evaluator result | Above plus the parity tests for the affected output |
| Lifecycle recommendation change | `python scripts/governance_check.py` plus `uv run pytest tests/test_lifecycle_recommendation.py tests/test_lifecycle_recommendation_rules.py tests/test_lifecycle.py tests/test_promotion.py` |
| Refactor that does not change observable behavior | `python scripts/governance_check.py` plus the full test suite (`uv run pytest`) |
| Dependency change (`pyproject.toml`, `uv.lock`) | Full mode governance check plus full test suite plus a manual `uv sync` to confirm the lockfile is consistent |

The implementation agent must run **at least** the minimum floor. The implementation agent may run additional checks when the change's risk profile demands them.

### 3. The Governance Check Gate

`scripts/governance_check.py` is the executable gate that records the harness's expectations. It runs in two modes.

- `--quick` — runs the two minimum checks: `openspec validate --strict --all` and `uv run skill-forge --help`. The quick mode is the floor for a docs-only change.
- Full (default) — runs the quick checks plus `openspec schema validate`, the two example-change strict validations, and `uv run pytest`. The full mode is the floor for any code, schema, or governance change.

The script prints one PASS or FAIL line per check and a summary line `Summary: N passed, 0 failed, 0 skipped`. A failing check is a stop condition. The implementation agent reports the failure with: command, exit code, error excerpt, suspected cause, and proposed next step.

### 4. How to Run Targeted Tests

- One test file: `uv run pytest tests/test_<name>.py`.
- One test function: `uv run pytest tests/test_<name>.py::test_<func>`.
- One test class: `uv run pytest tests/test_<name>.py::TestClass`.
- Tests by keyword: `uv run pytest -k "<keyword>"`.
- Tests with output: `uv run pytest -s`.
- Stop at first failure: `uv run pytest -x`.
- Show the slowest N tests: `uv run pytest --durations=N`.

The implementation agent must run the targeted tests that cover the touched module(s) on every code change.

### 5. How to Run the Full Test Suite

`uv run pytest` runs the full suite. The implementation agent runs the full suite on every refactor and on every change that touches a shared module (a module imported by more than one other module). The agent records the pass/fail count and the total time in the change's `verification.md`.

### 6. How to Interpret Failures

A test failure is information, not a verdict. The implementation agent follows `systematic-debugging` from `SUPERPOWERS.md`:

1. Reproduce the failure first. The reproduction must be the same command, the same inputs, and the same environment as the failure.
2. Locate the root cause. Do not "fix" the symptom.
3. Add a regression test that would have caught the bug. The test must fail without the fix and pass with the fix.
4. Only then change the implementation.
5. Re-run the minimum verification floor plus the targeted test for the fix.

A test that fails for an environmental reason (missing tool, network, GPU) is recorded as `skipped-with-reason`, not as a `pass` or a `fail`. The change cannot be declared done while an environmental failure blocks any of the floor checks.

### 7. Recording Skipped or Failed Verification

Every change's `verification.md` (or, for docs-only changes outside an OpenSpec change, the change's record in the relevant doc) must include:

- The exact command run.
- The exit status.
- The observed output summary (one to three lines; full output is preserved in the change folder when relevant).
- For each `skipped` command, the reason (environmental, tool, blocked dependency).
- For each `failed` command, the suspected cause and the proposed next step. A failed floor check is a stop, not a soft warning.

The `## Skipped Commands` table format from the existing OpenSpec change folders is the canonical shape. A skipped command must explain its impact (`none` if the skip is benign, `blocking` if it would block the change from being declared done).

### 8. What Counts as Verification

| Counts as verification | Does not count as verification |
|---|---|
| `python scripts/governance_check.py --quick` exiting 0 | Reading a file and saying "looks right" |
| `python scripts/governance_check.py` exiting 0 with a recorded pass count | Running a single targeted test and declaring the suite green |
| `uv run pytest` exiting 0 with a recorded pass count | "It compiled" without tests |
| `uv run skill-forge --help` exiting 0 and printing the expected command list | Manually running a command in a chat transcript |
| `git push origin main` exiting 0 and a recorded `git log --oneline origin/main -N` | A green CI badge from a previous change |
| `openspec validate <change-id> --strict` printing `valid` | An OpenSpec change folder that exists but has empty artifacts |

Verification is the recorded exit code plus the recorded output, not the agent's confidence in the result.

## Related Files

- `docs/02-harness/harness-overview.md` — harness model.
- `docs/02-harness/agent-workflow.md` — per-agent workflow.
- `docs/01-architecture/data-flow.md` — per-flow verification commands.
- `docs/04-superpowers/execution-discipline.md` — TDD, debugging, verification.
- `scripts/governance_check.py` — the gate script.
- `openspec/changes/<change-id>/verification.md` — the per-change evidence record.

## What Not To Do

- Do not declare a change done without recorded evidence. "Looks good" is not verification.
- Do not use a lower verification floor than the one defined here. The floor is the minimum, not the maximum.
- Do not run the quick mode for a code change. The full mode is the floor for code.
- Do not skip a floor check without recording the reason and the impact.
- Do not let a failed floor check be a soft warning. A failure is a stop.
- Do not paper over a test failure by changing the test to match an implementation that does not satisfy the original requirement.
- Do not push to a remote as part of "verification". Pushing is a hand-off, not a check.
