# Proposal: add-governance-enforcement-hooks

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 4 (governance enforcement hooks)
> Date: 2026-06-06
>
> This is a small, additive governance-tooling change. It does
> not modify business code, schema, config, or pre-existing
> WIP. The pre-existing dirty worktree is preserved untouched.

## Why

Phases 0-3 established a full eight-artifact governance stack,
but the stack is still documentation-only: a contributor has to
remember which commands to run, in which order, with which
flags, to confirm that a change has passed the gates. A
lightweight local script turns those gates into a one-command
check that a weak agent can run end-to-end.

This is the first enforcement tool in the project. It must be
small enough that a reviewer can read it in one pass and run it
without installing new dependencies.

## What Changes

- Add a new script `scripts/governance_check.py` that runs the
  governance commands in sequence and prints PASS/FAIL/SKIP per
  command. The script uses only the Python standard library.
- Add a new test file `tests/test_governance_check.py` that
  unit-tests the script's command-list construction, result
  aggregation, exit-code behavior, and skip reporting, using
  monkeypatching and subprocess mocking.
- Add a new change folder
  `openspec/changes/add-governance-enforcement-hooks/` with the
  full eight governance artifacts.
- Add a new verification report
  `docs/00-project/governance-enforcement-verification-report.md`.

## Capabilities

### New Capabilities

- `governance-enforcement-hooks`: a one-command local check
  that runs the project's known governance gates. The full
  mode runs six commands; the `--quick` mode runs two. The
  script exits non-zero when any required command fails.
  Optional commands are skipped with a printed reason when
  the underlying tool is missing.

### Modified Capabilities

- None. No existing capability's requirements are changed by
  this slice.

### Removed Capabilities

- None.

## Impact

- Code: one new script `scripts/governance_check.py`. No
  business code under `src/` is modified. No existing
  governance file is modified.
- CLI: none. The script is a developer tool, not a CLI
  command. `uv run skill-forge --help` output is unchanged.
- Schemas: none. `openspec/config.yaml`,
  `openspec/schemas/**`, and `skill-forge.json` are not
  modified.
- Workspaces: none. The script does not read or write any
  workspace file.
- Dependencies: none. `pyproject.toml` and `uv.lock` are not
  modified. The script uses only the standard library.
- Tests: one new test file `tests/test_governance_check.py`.
  The test file uses `monkeypatch` and `subprocess` mocking;
  it does not invoke `openspec` or `uv` directly.
- OpenSpec tree: one new change folder is added under
  `openspec/changes/add-governance-enforcement-hooks/`. The
  change uses the `skill-forge-governance` schema.

## Non-Goals

- Pre-commit hook configuration. The Phase 4 taskbook
  forbids it, and adding it would require a new tool config
  file that is out of scope.
- CI integration. The Phase 4 taskbook forbids it, and adding
  it would require a new workflow file.
- Business functionality. The script is a governance tool; it
  does not change Skill Forge's runtime behavior.
- Modifying the OpenSpec schema. `openspec/schemas/**` is
  forbidden.
- Modifying the OpenSpec config. `openspec/config.yaml` is
  forbidden.
- Cleaning up the pre-existing dirty WIP. The dirty worktree
  is preserved untouched.
- Adapting the Phase 3 lifecycle recommendation service to
  use the new pure function. That adapter is Phase 5 work.
- Adding a per-command flag (e.g., `--only pytest`) to the
  script. A per-command flag is a follow-up.
- Color output. The script prints plain text only.

## Risks

- [The script may be invoked from a directory other than the
  repository root, and `git status --short` is not the
  script's job] -> Mitigation: the script resolves all
  command paths relative to the directory the script is
  invoked from. The verification report records the working
  directory for every command.
- [The script may run for a long time because `uv run pytest`
  is part of full mode] -> Mitigation: `--quick` mode
  excludes `uv run pytest` and runs only the two fastest
  gates. The verification report records the elapsed time
  of full mode so the user can decide whether to run
  `--quick` instead.
- [A new contributor may run the script from inside a
  sub-directory and see misleading results] -> Mitigation:
  the script's docstring and `--help` text say "run from
  the repository root". The verification report records the
  exact working directory used to produce the recorded
  results.
- [The script's command list may drift from the actual
  governance gates as the project evolves] -> Mitigation:
  the command list is a single list-of-dicts in the script
  body, and a unit test asserts the exact full-mode and
  quick-mode command lists. Any drift fails the unit test.

## Rollback

1. Delete the file `scripts/governance_check.py`.
2. Delete the file `tests/test_governance_check.py`.
3. Delete the folder
   `openspec/changes/add-governance-enforcement-hooks/`.
4. Delete the file
   `docs/00-project/governance-enforcement-verification-report.md`.
5. No data migration. The script did not write to disk.
6. No business code, schema, or config was changed, so no
   rollback is needed outside the four files above.

## Consistency With Brainstorm

- Brainstorm file: `brainstorm.md` (in this folder).
- Recommended option: Option A (a local Python script
  `scripts/governance_check.py` with a unit test file and a
  full eight-artifact change folder).
- Deviations and reasons: none. The proposal implements
  Option A exactly as the brainstorm describes it.
