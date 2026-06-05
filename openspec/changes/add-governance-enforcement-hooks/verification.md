# Verification: add-governance-enforcement-hooks

> Status: draft
> Schema: skill-forge-governance
> Depends on: tasks.md
>
> Verification is written AT THE END of the change, after
> tasks are complete, not before. A change without a
> verification record is not done.

## Change Id

`add-governance-enforcement-hooks`

## Executed Commands

### `git status --short`

- Working directory: repository root.
- Exit code: 0.
- Output summary: the new untracked Phase 4 paths are visible
  (the new `openspec/changes/add-governance-enforcement-hooks/`
  folder, the new `scripts/governance_check.py` file, the new
  `tests/test_governance_check.py` file, and the new
  `docs/00-project/governance-enforcement-verification-report.md`
  file). The pre-existing WIP is unchanged.

### `git diff --name-only`

- Working directory: repository root.
- Exit code: 0.
- Output summary: only the pre-existing dirty WIP paths are
  listed. The Phase 4 files are untracked and therefore do
  not appear in `git diff --name-only`. The pre-existing
  WIP paths are out of scope for Phase 4.

### `openspec validate add-governance-enforcement-hooks --strict`

- Working directory: repository root.
- Exit code: 0.
- Output summary: `Change 'add-governance-enforcement-hooks' is valid`.

### `openspec validate --strict --all`

- Working directory: repository root.
- Exit code: 0.
- Output summary: 25 items passed, 0 failed (25 items). The
  new change is included in the passed list alongside the
  Phase 3 `add-skill-lifecycle-recommendation` change, the
  example `example-governance-stack-walkthrough` change, and
  22 existing specs.

### `uv run pytest tests/test_governance_check.py`

- Working directory: repository root.
- Exit code: 0.
- Output summary: 24 tests collected, 24 passed, 0 failed,
  0 skipped. The full set of unit tests for the governance
  check script is green.

### `uv run pytest`

- Working directory: repository root.
- Exit code: 0.
- Output summary: `============================ 304 passed in 17.53s =============================`.
  Before Phase 4, the suite contained 280 tests; the 24
  new tests in `tests/test_governance_check.py` are added
  on top of the pre-existing WIP tests.

### `uv run skill-forge --help`

- Working directory: repository root.
- Exit code: 0.
- Output summary: the CLI loads and lists its commands. No
  new command is added by this slice; the pre-existing CLI
  surface is preserved.

### `python scripts/governance_check.py --quick`

- Working directory: repository root.
- Exit code: 0.
- Output summary: `[PASS] openspec validate --strict --all (required)`
  + `[PASS] uv run skill-forge --help (required)`,
  `Summary: 2 passed, 0 failed, 0 skipped`.

### `python scripts/governance_check.py` (full mode)

- Working directory: repository root.
- Exit code: 0.
- Output summary: 6 PASS lines, `Summary: 6 passed, 0 failed,
  0 skipped`. The full mode runs all six required governance
  commands and exits 0.

## Test Results

- Test framework: pytest.
- Collected: 304.
- Passed: 304.
- Failed: 0.
- Skipped: 0.
- Summary: `============================ 304 passed in 17.53s =============================`.

## OpenSpec Validation

- Command: `openspec validate add-governance-enforcement-hooks --strict`.
- Result: `valid`.
- Summary: the change passes strict validation under the
  `skill-forge-governance` schema. All eight required
  artifacts (`brainstorm`, `proposal`, `spec`, `design`,
  `review`, `plan`, `tasks`, `verification`) are present
  and conform to the template.

## Skipped Commands

| Command       | Reason     | Impact    |
|---------------|------------|-----------|
| `openspec archive add-governance-enforcement-hooks` | The change is not archived in Phase 4. Archiving is the start of a later phase and is out of scope here. | none |
| Optional-skip path on a missing tool | Not triggered during the recorded runs. The path is exercised by the unit tests but did not trigger here. | none |

## Deviations from Plan

- Planned: create the eight OpenSpec artifacts, the script,
  the test file, and the verification report.
- Actual: same files. One small implementation note: the
  script uses a Windows-aware `_should_use_shell` helper to
  invoke `.CMD` files through the user's shell. This was
  added because the recorded environment is Windows; without
  the helper, `subprocess.run` raises `FileNotFoundError` for
  `.CMD` files even when they exist on `PATH`. The helper is
  unit-tested and the cross-platform behavior is preserved.
- Reason: the helper is required for the script to run on
  Windows. The helper is small and does not change the
  script's public API or its command list.

## Remaining Risks

- [The script's command list may drift from the project's
  actual governance gates] -> Mitigation: a unit test
  asserts the exact full-mode and quick-mode command lists.
- [The script is not yet wired into CI or pre-commit]
  -> Mitigation: this is an explicit non-goal for Phase 4.
- [Pre-existing WIP in the working tree was not cleaned up]
  -> Mitigation: the Phase 4 task explicitly forbids
  cleaning the pre-existing WIP.

## Follow-up Changes

- Phase 5 should consolidate the Phase 3 lifecycle
  recommendation service and the Phase 3 pure function
  `recommend_lifecycle_action` into a single, deterministic
  rule path. The recommended steps are listed in
  `docs/00-project/governance-enforcement-verification-report.md`
  Section 14.
- A future phase may wire `scripts/governance_check.py` into
  a CI workflow. That change is out of scope for Phase 4.

## Verdict

`done`
