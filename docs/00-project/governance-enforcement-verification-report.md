# Phase 4 Verification Report: Governance Enforcement Hooks

> Status: done
> Phase: 4
> Date: 2026-06-06
> Schema: skill-forge-governance
> Commit (this report): see "Commit SHA" section

This report records the verification of the Phase 4 change
`add-governance-enforcement-hooks`. The change adds a
lightweight, stdlib-only local governance check script and a
companion unit test file, both under the strict-scope allowed
path list. The change does not modify business code, the
OpenSpec schema or config, the Phase 3 lifecycle files, or any
pre-existing WIP.

## 1. Phase 4 Goal

Add lightweight local governance enforcement so the governance
stack is no longer documentation-only. The change must not
expand business functionality.

## 2. Selected Implementation Strategy

A stdlib-only Python script `scripts/governance_check.py` plus
a unit test file `tests/test_governance_check.py`, accompanied
by a full eight-artifact OpenSpec change folder and a Phase 4
verification report. The script uses only the Python standard
library; no third-party dependency is added; `pyproject.toml`
and `uv.lock` are not modified.

## 3. Changed Files (Phase 4)

The following files were created or modified by this phase:

- `openspec/changes/add-governance-enforcement-hooks/.openspec.yaml`
- `openspec/changes/add-governance-enforcement-hooks/brainstorm.md`
- `openspec/changes/add-governance-enforcement-hooks/proposal.md`
- `openspec/changes/add-governance-enforcement-hooks/design.md`
- `openspec/changes/add-governance-enforcement-hooks/review.md`
- `openspec/changes/add-governance-enforcement-hooks/plan.md`
- `openspec/changes/add-governance-enforcement-hooks/tasks.md`
- `openspec/changes/add-governance-enforcement-hooks/verification.md`
- `openspec/changes/add-governance-enforcement-hooks/specs/governance-enforcement-hooks/spec.md`
- `scripts/governance_check.py`
- `tests/test_governance_check.py`
- `docs/00-project/governance-enforcement-verification-report.md` (this file)

## 4. Restricted Path Check

The Phase 4 allowed-path list was respected. None of the
forbidden paths listed in the Phase 4 task were touched. The
following paths are explicitly **not** in the Phase 4 diff:

- `src/**` (untouched)
- `tests/test_lifecycle_recommendation_rules.py` (untouched)
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md` (untouched)
- `README.md`, `README.zh-CN.md` (untouched)
- `docs/03-openspec/**`, `docs/04-superpowers/**`, `.superpowers/**` (untouched)
- `openspec/config.yaml`, `openspec/schemas/**` (untouched)
- `openspec/changes/example-governance-stack-walkthrough/**` (untouched)
- `openspec/changes/add-skill-lifecycle-recommendation/**` (untouched)
- `templates/**`, `configs/**` (untouched)
- `pyproject.toml`, `uv.lock` (untouched)

Verdict: **forbidden paths changed: no**.

## 5. Dirty Worktree Handling

The repository contained a substantial pre-existing dirty
worktree at the start of Phase 4. The pre-existing
modifications were preserved untouched. They are not in the
Phase 4 diff and are not included in the Phase 4 commit. The
following pre-existing dirty entries were observed and left
untouched (sample, not exhaustive):

- Modifications under `src/skill_forge/`: `cli.py`, `config.py`,
  `llm/refiner.py`, `models/generated.py`, `models/quality.py`,
  `models/search.py`, `retrieval/retriever.py`,
  `storage/corpus_reader.py`, `storage/paths.py`.
- Modifications under `tests/`: `test_cli.py`,
  `test_generation_quality_report.py`, `test_llm_refiner.py`,
  `test_search_retrieval.py`, `test_skill_library.py`.
- Modifications under `docs/`: `skill_forge_next_evolution_plan.md`,
  `skill_generation_roadmap.md`.
- Modifications under `openspec/specs/`: `generation-quality-report`,
  `llm-assisted-generation`, `local-skill-generation`,
  `search-retrieval`, `skill-evaluation`,
  `skill-library-management`, `skill-validation`.
- Deletions under `openspec/changes/add-community-skill-discovery/`.
- Untracked directories: `.claude/`, `.codex/`, `AGENT.md`,
  multiple new spec directories, multiple archive directories,
  new files under `src/skill_forge/` (adoption, experience,
  lifecycle, models, retrieval), new test files, and
  pre-existing Phase 4 input files such as
  `docs/rectification/skill-forge-phase-4-governance-enforcement-hooks-taskbook.md`.

The Phase 4 commit is staged with explicit `git add <path>`
commands for each Phase 4 path. No `git add .` or `git add -A`
is used. None of the pre-existing dirty entries are included in
the Phase 4 commit.

## 6. OpenSpec Change Summary

The change folder
`openspec/changes/add-governance-enforcement-hooks/`
declares `schema: skill-forge-governance` and contains the
full eight artifacts:

- `.openspec.yaml`
- `brainstorm.md`
- `proposal.md`
- `design.md`
- `review.md`
- `plan.md`
- `tasks.md`
- `verification.md`
- `specs/governance-enforcement-hooks/spec.md`

The capability name in the proposal matches the spec file
folder (`governance-enforcement-hooks`). The change adds one
new capability (`governance-enforcement-hooks`) and does not
modify any existing capability.

The `review.md` verdict is `approve`. The `plan.md` is the
executable contract and lists the allowed and forbidden paths
explicitly. The `verification.md` is the OpenSpec-level
evidence record for the change.

## 7. Governance Check Script Summary

`scripts/governance_check.py` is a stdlib-only Python script
that exposes the following entry points:

- `build_command_list(quick: bool) -> list[Command]` returns
  the six-command full-mode list or the two-command `--quick`
  list.
- `run_command(cmd: dict, cwd: str) -> Result` runs a single
  command via `subprocess.run`, captures the exit code, and
  returns a result dict.
- `summarize_results(commands, results) -> Summary` aggregates
  per-command results into a single summary, with a non-zero
  exit code when any required command failed or any required
  command was skipped due to a missing tool.
- `format_status_line(cmd, result) -> str` formats a single
  `[STATUS] label (required|optional)` line for printing.
- `main(argv) -> int` parses `--quick`, runs the gate suite,
  prints one line per command plus a summary line, and returns
  the exit code.

The script supports a `--quick` mode that runs only
`openspec validate --strict --all` and
`uv run skill-forge --help`. The full mode additionally runs
`openspec schema validate`,
`openspec validate example-governance-stack-walkthrough --strict`,
`openspec validate add-skill-lifecycle-recommendation --strict`,
and `uv run pytest`. The script never modifies the
repository; a unit test asserts that the working directory's
file list is unchanged after a run.

## 8. Test Summary

`tests/test_governance_check.py` contains 24 unit tests that
cover, at minimum, the six areas required by the Phase 4
task:

- Command-list construction (full mode): `test_full_mode_command_list`.
- Command-list construction (quick mode): `test_quick_mode_command_list`,
  `test_quick_mode_excludes_pytest`.
- Result aggregation: `test_summarize_results_all_pass`,
  `test_summarize_results_required_failure_returns_nonzero`,
  `test_summarize_results_optional_skip_does_not_block`,
  `test_summarize_results_required_skip_blocks`.
- Failed command returns non-zero:
  `test_summarize_results_required_failure_returns_nonzero`,
  `test_main_returns_nonzero_on_required_failure`.
- Skipped optional command is reported:
  `test_run_command_skips_when_tool_missing`,
  `test_status_line_includes_skip_reason`.
- Script does not mutate files:
  `test_script_does_not_mutate_files`,
  `test_script_writes_nothing_to_cwd`,
  `test_script_uses_only_stdlib`.

The tests use `monkeypatch` and `unittest.mock` to substitute
the subprocess runner; no real `openspec` or `uv` invocation
is performed inside the unit tests. The tests run in
0.10s.

## 9. Verification Command Results

| Command                                                              | Exit Code | Output Summary                                                                                  |
|----------------------------------------------------------------------|-----------|-------------------------------------------------------------------------------------------------|
| `git status --short`                                                 | 0         | The new untracked Phase 4 paths are visible; the pre-existing WIP is unchanged.                  |
| `git diff --name-only`                                               | 0         | Only the pre-existing dirty WIP paths are listed; Phase 4 files are untracked.                   |
| `openspec validate add-governance-enforcement-hooks --strict`         | 0         | `Change 'add-governance-enforcement-hooks' is valid`.                                            |
| `openspec validate --strict --all`                                   | 0         | 25 items passed, 0 failed (25 items). The new change is included in the passed list.            |
| `uv run pytest`                                                      | 0         | 304 passed in 17.53s.                                                                           |
| `uv run pytest tests/test_governance_check.py`                       | 0         | 24 passed in 0.10s.                                                                             |
| `uv run skill-forge --help`                                          | 0         | CLI loads; pre-existing commands are unchanged.                                                  |
| `python scripts/governance_check.py --quick`                         | 0         | `[PASS] openspec validate --strict --all (required)` + `[PASS] uv run skill-forge --help (required)`. |
| `python scripts/governance_check.py` (full)                          | 0         | 6 PASS lines, summary `6 passed, 0 failed, 0 skipped`.                                          |

## 10. Quick and Full Governance Check Results

### 10.1 Quick mode (`--quick`)

- `[PASS] openspec validate --strict --all (required)`
- `[PASS] uv run skill-forge --help (required)`
- `Summary: 2 passed, 0 failed, 0 skipped`
- Exit code: 0

### 10.2 Full mode (default)

- `[PASS] openspec schema validate (required)`
- `[PASS] openspec validate example-governance-stack-walkthrough --strict (required)`
- `[PASS] openspec validate add-skill-lifecycle-recommendation --strict (required)`
- `[PASS] openspec validate --strict --all (required)`
- `[PASS] uv run skill-forge --help (required)`
- `[PASS] uv run pytest (required)`
- `Summary: 6 passed, 0 failed, 0 skipped`
- Exit code: 0

## 11. Skipped Commands and Reasons

No commands in the script's command list were skipped during
the recorded runs. The optional-skip path is exercised by the
unit tests but did not trigger during this verification.

## 12. Implementation Notes

- The script uses a Windows-aware `_should_use_shell` helper
  to invoke `openspec.CMD` through the user's shell on
  Windows. Without this, `subprocess.run` on Windows raises
  `FileNotFoundError` for `.CMD` files even when they exist on
  `PATH`. The helper is unit-tested and the cross-platform
  behavior is verified.
- The script does not read or write any file in the
  repository. Two unit tests assert that the working
  directory's file list is unchanged after a run.
- The script's command list is a single list-of-dicts at the
  top of `scripts/governance_check.py`. A unit test asserts
  the exact full-mode and quick-mode command lists, so a
  future drift fails the test.

## 13. Remaining Risks

- [The script's command list may drift from the project's
  actual governance gates] -> Mitigation: a unit test asserts
  the exact full-mode and quick-mode command lists. Any
  drift fails the unit test.
- [The script is not yet wired into CI or pre-commit]
  -> Mitigation: this is an explicit non-goal for Phase 4.
  Wiring the script into CI is a follow-up change.
- [A future change may add a per-command flag, and the unit
  tests will need to be updated] -> Mitigation: a per-command
  flag is a follow-up. The unit tests assert the exact
  command lists at Phase 4.
- [Pre-existing WIP in the working tree was not cleaned up]
  -> Mitigation: the Phase 4 task explicitly forbids cleaning
  the pre-existing WIP. The WIP is preserved untouched and
  is not included in the Phase 4 commit.

## 14. Recommended Phase 5

Phase 5 should consolidate the Phase 3 lifecycle recommendation
service and the Phase 3 pure function `recommend_lifecycle_action`
into a single, deterministic rule path. The recommended steps
are:

- Adapt `src/skill_forge/lifecycle/recommendation.py` so that
  the service-level `LifecycleRecommendationService` calls the
  pure function `recommend_lifecycle_action` from
  `src/skill_forge/lifecycle/recommendation_rules.py`.
- Add a parity test that compares the service-level
  recommendation to the pure-function recommendation for the
  same `LifecycleSummary`.
- Preserve the public API of the service. No new CLI
  commands. No new business functionality.
- Add a new OpenSpec change folder
  `openspec/changes/add-lifecycle-recommendation-service-adapter/`
  and run the full eight-artifact flow under
  `skill-forge-governance`.
- Verify with `python scripts/governance_check.py` (full mode)
  before commit.

## 15. Commit Recommendation

The change is recommended for commit. The script, the test
file, the OpenSpec change folder, and this report are
collectively a small, additive, self-contained governance
tooling slice. The OpenSpec validation, the pytest suite, the
CLI smoke test, and both governance check modes all pass. The
Phase 4 forbidden paths are untouched. The pre-existing WIP is
preserved.

## 16. Commit SHA

The Phase 4 change is committed as `0bcd73f` with the message
`chore: add governance enforcement check`. A follow-up docs
commit (`<see git log>`) records the SHA in
`openspec/changes/add-governance-enforcement-hooks/verification.md`.
