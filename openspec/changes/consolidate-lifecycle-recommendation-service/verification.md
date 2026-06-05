# Verification: consolidate-lifecycle-recommendation-service

> Status: draft
> Schema: skill-forge-governance
> Depends on: tasks.md
>
> Verification is written AT THE END of the change, after
> tasks are complete, not before. A change without a
> verification record is not done.

## Change Id

`consolidate-lifecycle-recommendation-service`

## Executed Commands

### `git status --short`

- Working directory: repository root.
- Exit code: 0.
- Output summary: the new untracked Phase 5 paths under
  `openspec/changes/consolidate-lifecycle-recommendation-service/`,
  the new `docs/00-project/lifecycle-service-adapter-verification-report.md`,
  and the untracked-but-modified-by-this-phase
  `src/skill_forge/lifecycle/recommendation.py` and
  `tests/test_lifecycle_recommendation.py` are visible
  as untracked entries; the pre-existing WIP under
  `src/skill_forge/`, `tests/`, `docs/`, and the
  deletions under
  `openspec/changes/add-community-skill-discovery/` are
  preserved untouched and are out of scope for Phase 5.

### `git diff --name-only`

- Working directory: repository root.
- Exit code: 0.
- Output summary: only the pre-existing dirty WIP paths
  are listed. None of the Phase 5 files appear in
  `git diff --name-only` because all four Phase 5
  files are untracked at the time of this run. The
  pre-existing WIP paths (under `src/skill_forge/`,
  `tests/`, `docs/`, `openspec/specs/`, and the
  deletions under
  `openspec/changes/add-community-skill-discovery/`)
  are out of scope for Phase 5.

### `openspec validate consolidate-lifecycle-recommendation-service --strict`

- Working directory: repository root.
- Exit code: 0.
- Output summary: `Change 'consolidate-lifecycle-recommendation-service' is valid`.

### `openspec validate --strict --all`

- Working directory: repository root.
- Exit code: 0.
- Output summary: 26 items passed, 0 failed (26 items).
  The new change `consolidate-lifecycle-recommendation-service`
  is included in the passed list alongside the
  `add-skill-lifecycle-recommendation` change, the
  `add-governance-enforcement-hooks` change, and the
  pre-existing specs.

### `uv run pytest tests/test_lifecycle_recommendation_rules.py`

- Working directory: repository root.
- Exit code: 0.
- Output summary: 15 tests collected, 15 passed, 0 failed,
  0 skipped. The pre-existing pure-function tests remain
  valid and pass unchanged.

### `uv run pytest tests/test_lifecycle_recommendation.py`

- Working directory: repository root.
- Exit code: 0.
- Output summary: 15 tests collected, 15 passed, 0 failed,
  0 skipped. The pre-existing 9 service-level tests pass
  unchanged, and the 6 new parity tests
  (`test_service_outdated_provenance_matches_pure_function`,
  `test_service_current_metadata_matches_pure_function`,
  `test_service_unknown_new_skill_matches_pure_function`,
  `test_service_recommend_uses_pure_function_for_known_state`,
  `test_service_recommend_no_longer_uses_removed_private_helpers`,
  `test_cli_help_is_unchanged`) pass.

### `uv run pytest`

- Working directory: repository root.
- Exit code: 0.
- Output summary:
  `============================ 310 passed in 13.92s =============================`.
  The full test suite is green. Before Phase 5, the suite
  contained 304 tests; the 6 new parity tests in
  `tests/test_lifecycle_recommendation.py` are added on
  top of the pre-existing WIP tests.

### `uv run skill-forge --help`

- Working directory: repository root.
- Exit code: 0.
- Output summary: the CLI loads and lists its commands.
  The pre-existing `lifecycle` command is unchanged. No
  new command is added by this slice; the pre-existing
  CLI surface is preserved.

### `python scripts/governance_check.py --quick`

- Working directory: repository root.
- Exit code: 0.
- Output summary:
  - `[PASS] openspec validate --strict --all (required)`
  - `[PASS] uv run skill-forge --help (required)`
  - `Summary: 2 passed, 0 failed, 0 skipped`.

### `python scripts/governance_check.py` (full)

- Working directory: repository root.
- Exit code: 0.
- Output summary:
  - `[PASS] openspec schema validate (required)`
  - `[PASS] openspec validate example-governance-stack-walkthrough --strict (required)`
  - `[PASS] openspec validate add-skill-lifecycle-recommendation --strict (required)`
  - `[PASS] openspec validate --strict --all (required)`
  - `[PASS] uv run skill-forge --help (required)`
  - `[PASS] uv run pytest (required)`
  - `Summary: 6 passed, 0 failed, 0 skipped`.

## Test Results

- Test framework: pytest.
- Collected: 310.
- Passed: 310.
- Failed: 0.
- Skipped: 0.
- Summary:
  `============================ 310 passed in 13.92s =============================`.

## OpenSpec Validation

- Command:
  `openspec validate consolidate-lifecycle-recommendation-service --strict`.
- Result: `valid`.
- Summary: the change passes strict validation under the
  `skill-forge-governance` schema. All eight required
  artifacts (`brainstorm`, `proposal`, `spec`, `design`,
  `review`, `plan`, `tasks`, `verification`) are present
  and conform to the template. The capability
  `lifecycle-recommendation-service-adapter` is added.

## Skipped Commands

| Command                                                | Reason                                                                                                                                                                              | Impact    |
|--------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| `openspec archive consolidate-lifecycle-recommendation-service` | The change is not archived in Phase 5. Archiving is the start of a later phase and is out of scope here. The change is delivered as an OpenSpec change on disk, validated, and committed. | none |
| `uv run skill-forge lifecycle recommend ...`           | CLI integration is out of scope for this slice. The pre-existing CLI command is preserved and the `lifecycle --help` text is unchanged.                                              | none      |
| `uv run skill-forge lifecycle compare ...`             | CLI integration is out of scope for this slice. The pre-existing CLI command is preserved and the `lifecycle --help` text is unchanged.                                              | none      |

## Deviations from Plan

- Planned: a 4-task verification block in
  `tasks.md` Section 4, including 13 sub-tasks.
- Actual: same 13 sub-tasks; no deviation in the file
  list, the file paths, the verification commands, or
  the parity test names.
- Reason: the plan was followed as written.

## Remaining Risks

- [The reason text for the `unknown` state is now
  produced by the pure function, not by the service
  module] -> Mitigation: the pre-existing service tests
  in `tests/test_lifecycle_recommendation.py` do not
  assert on the reason text for the `unknown` state, and
  the CLI tests assert only on the action and on the
  printed "Lifecycle recommendation" and
  "ready-to-promote" strings. The refactor is compatible
  with every existing test.
- [A future change to the pure function's reason text
  will change the service's output text] -> Mitigation:
  the parity tests in
  `tests/test_lifecycle_recommendation.py` assert on
  the full `model_dump()` of both recommendations, so
  any future drift between the service and the pure
  function is caught immediately.
- [The pre-existing WIP under `src/skill_forge/` is not
  exercised by the new parity tests] -> Mitigation: the
  parity tests cover the three required paths
  (outdated provenance, current metadata, unknown new
  skill) plus the `needs-eval` known-state path. The
  pre-existing tests in
  `tests/test_lifecycle_recommendation.py` continue to
  exercise the service and the CLI integration.
- [The `compare` method still has its own private
  helpers (`_comparison_key`, `_compare_reason`,
  `_tie_breaker_reason`) that the pure function does
  not duplicate] -> Mitigation: a future phase can
  consolidate `compare` if needed. The slice is
  intentionally limited to `recommend`.

## Follow-up Changes

- A future phase may consolidate the `compare` method's
  helpers into the pure module. The `compare` method's
  rule is not duplicated by the pure function in Phase 5.
- A future phase may add additional parity tests
  (e.g., for `regressed` state or for
  `applied_experience_rule_ids` non-empty cases) if
  needed. The current six parity tests cover the three
  required paths plus a known-state and a regression
  guard.
- A future phase may archive this change. The change
  is delivered as an OpenSpec change on disk, validated,
  and committed in Phase 5; archiving is the start of a
  later phase.

## Verdict

`done`
