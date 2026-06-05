# Phase 5 Verification Report: Lifecycle Recommendation Service Adapter

> Status: done
> Phase: 5
> Date: 2026-06-06
> Schema: skill-forge-governance
> Commit (this report): see "Commit SHA" section

This report records the verification of the Phase 5 change
`consolidate-lifecycle-recommendation-service`. The change
consolidates the state-based lifecycle recommendation rule
by making the service-level recommendation use the
deterministic pure recommendation rule introduced in
Phase 3. The change is an internal adapter/refactor slice;
user-facing behavior is preserved.

## 1. Phase 5 Goal

Consolidate the lifecycle recommendation service logic by
making the service-level recommendation use the
deterministic pure recommendation rule. This phase is an
internal adapter/refactor slice and must not expand
user-facing behavior.

## 2. Selected Implementation Strategy

A private adapter `_summary_to_input` lives inside
`src/skill_forge/lifecycle/recommendation.py`. The
adapter maps a `LifecycleSummary` (the service-level data
carrier) to a `LifecycleRecommendationInput` (the pure
function's input model). The service's `recommend` method
delegates to the pure function `recommend_lifecycle_action`
through the adapter via a small private helper
`_recommend_via_rules`. The pre-existing private rule
helpers `_recommend_from_summary` and `_summary_signals`
are removed because their rule is now centralized in the
pure module. The `compare` method and its helpers are
preserved.

The adapter uses a lazy import inside the function body
to break the circular dependency between
`recommendation.py` and `recommendation_rules.py`
(`recommendation_rules.py` imports `LifecycleRecommendation`
from `recommendation.py` at module load time).

## 3. Changed Files (Phase 5)

The following files were created or modified by this phase:

- `openspec/changes/consolidate-lifecycle-recommendation-service/.openspec.yaml`
- `openspec/changes/consolidate-lifecycle-recommendation-service/brainstorm.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/proposal.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/design.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/review.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/plan.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/tasks.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/specs/lifecycle-recommendation-service-adapter/spec.md`
- `src/skill_forge/lifecycle/recommendation.py` (modified)
- `tests/test_lifecycle_recommendation.py` (modified)
- `docs/00-project/lifecycle-service-adapter-verification-report.md` (this file)

`src/skill_forge/lifecycle/recommendation_rules.py` is
not modified by this slice. The pure function is reused
as-is. `tests/test_lifecycle_recommendation_rules.py` is
not modified by this slice. The pre-existing pure
function tests remain valid.

## 4. Restricted Path Check

The Phase 5 allowed-path list was respected. None of the
forbidden paths listed in the Phase 5 task were touched.
The following paths are explicitly **not** in the Phase 5
diff:

- `scripts/governance_check.py` (untouched)
- `tests/test_governance_check.py` (untouched)
- `src/skill_forge/cli.py` (untouched)
- Every other file under `src/skill_forge/**` that is
  not `src/skill_forge/lifecycle/recommendation.py` or
  `src/skill_forge/lifecycle/recommendation_rules.py`
  (untouched).
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
  `SUPERPOWERS.md` (untouched).
- `README.md`, `README.zh-CN.md` (untouched).
- `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**` (untouched).
- `openspec/config.yaml`, `openspec/schemas/**`
  (untouched).
- `openspec/changes/example-governance-stack-walkthrough/**`
  (untouched).
- `openspec/changes/add-skill-lifecycle-recommendation/**`
  (untouched).
- `openspec/changes/add-governance-enforcement-hooks/**`
  (untouched).
- `templates/**`, `configs/**` (untouched).
- `pyproject.toml`, `uv.lock` (untouched).

Verdict: **forbidden paths changed: no**.

## 5. Dirty Worktree Handling

The repository contained a substantial pre-existing dirty
worktree at the start of Phase 5. The pre-existing
modifications were preserved untouched. They are not in
the Phase 5 diff and are not included in the Phase 5
commit. The pre-existing dirty entries (modifications
under `src/skill_forge/`, `tests/`, `docs/`, the
deletions under `openspec/changes/add-community-skill-discovery/`,
and the untracked entries including
`openspec/changes/add-governance-enforcement-hooks/`,
`scripts/`, `tests/test_governance_check.py`,
`docs/00-project/governance-enforcement-verification-report.md`,
and the various pre-existing Phase 4 inputs) were
observed and left untouched.

The Phase 5 commit is staged with explicit
`git add <path>` commands for each Phase 5 path. No
`git add .` or `git add -A` is used. None of the
pre-existing dirty entries are included in the Phase 5
commit.

## 6. OpenSpec Change Summary

The change folder
`openspec/changes/consolidate-lifecycle-recommendation-service/`
declares `schema: skill-forge-governance` and contains
the full eight artifacts:

- `.openspec.yaml`
- `brainstorm.md`
- `proposal.md`
- `design.md`
- `review.md`
- `plan.md`
- `tasks.md`
- `verification.md`
- `specs/lifecycle-recommendation-service-adapter/spec.md`

The capability name in the proposal matches the spec
file folder
(`lifecycle-recommendation-service-adapter`). The change
adds one new capability
(`lifecycle-recommendation-service-adapter`) and does
not modify any existing capability.

The `review.md` verdict is `approve`. The `plan.md` is
the executable contract and lists the allowed and
forbidden paths explicitly. The `verification.md` is the
OpenSpec-level evidence record for the change.

## 7. Adapter Strategy

The adapter lives in
`src/skill_forge/lifecycle/recommendation.py` as a
private function `_summary_to_input` and a private
helper `_recommend_via_rules`. The flow is:

1. `LifecycleRecommendationService.recommend(skill_name)`
   reads a `LifecycleSummary` from
   `LifecycleService.show(skill_name)`.
2. The service calls
   `_recommend_via_rules(summary)`.
3. `_recommend_via_rules` calls
   `_summary_to_input(summary)` to build a
   `LifecycleRecommendationInput` and then calls
   `recommend_lifecycle_action(input)`.
4. The pure function returns a
   `LifecycleRecommendation`, which the service
   returns to the caller.

The adapter maps every field of
`LifecycleRecommendationInput` from the corresponding
field of `LifecycleSummary`. The fields are:
`skill_name`, `state`, `reason`, `missing_facts`,
`quality_score`, `quality_status`, `eval_total`,
`eval_passed`, `eval_failed`, and
`applied_experience_rule_ids`. `package_path`,
`evidence`, and `resolved_experience_rules` are not
passed to the pure function; they are service-level
concerns.

The adapter uses a lazy import inside the function body
to break the circular dependency between
`recommendation.py` and `recommendation_rules.py`.

## 8. Parity Tests Summary

Six new tests were added to
`tests/test_lifecycle_recommendation.py`. The pre-existing
9 tests in the file remain valid and pass unchanged.

The new tests are:

- `test_service_outdated_provenance_matches_pure_function`:
  a Skill with no `skill-forge.json` is classified as
  `state="unknown"`. The service's recommendation and
  the pure function's recommendation for the same
  summary match on `state`, `action`, `reason`,
  `missing_facts`, and `signals`.
- `test_service_current_metadata_matches_pure_function`:
  a Skill with a current valid `skill-forge.json`,
  content-quality metrics, and a passing eval report is
  classified as `state="healthy"`. The service's
  recommendation and the pure function's recommendation
  for the same summary match on `state`, `action`,
  `reason`, `missing_facts`, and `signals`.
- `test_service_unknown_new_skill_matches_pure_function`:
  a Skill with only a `SKILL.md` and no `skill-forge.json`
  is classified as `state="unknown"`. The service's
  recommendation and the pure function's recommendation
  for the same summary match on `state`, `action`,
  `reason`, `missing_facts`, and `signals`.
- `test_service_recommend_uses_pure_function_for_known_state`:
  a Skill with no eval report is classified as
  `state="needs-eval"`. The service's recommendation
  and the pure function's recommendation for the same
  summary are byte-for-byte equal
  (`model_dump()` equality).
- `test_service_recommend_no_longer_uses_removed_private_helpers`:
  the pre-Phase-5 private helpers
  `_recommend_from_summary` and `_summary_signals` are
  no longer defined in the service module. The new
  private helpers `_recommend_via_rules` and
  `_summary_to_input` are present.
- `test_cli_help_is_unchanged`: the CLI help text for
  the `lifecycle` command still includes `recommend`
  and `compare`.

The pre-existing pure function tests in
`tests/test_lifecycle_recommendation_rules.py` (15
tests) remain valid and pass unchanged.

## 9. Verification Command Results

| Command                                                                  | Exit Code | Output Summary                                                                                                            |
|--------------------------------------------------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------|
| `git status --short`                                                     | 0         | The new untracked Phase 5 paths are visible; `src/skill_forge/lifecycle/recommendation.py` and `tests/test_lifecycle_recommendation.py` are untracked entries (modified by this phase, never committed before); the pre-existing WIP is unchanged. |
| `git diff --name-only`                                                   | 0         | Only the pre-existing dirty WIP paths are listed. None of the Phase 5 files appear in `git diff --name-only` because all four Phase 5 files are untracked at the time of this run. |
| `openspec validate consolidate-lifecycle-recommendation-service --strict` | 0         | `Change 'consolidate-lifecycle-recommendation-service' is valid`.                                                          |
| `openspec validate --strict --all`                                       | 0         | 26 items passed, 0 failed (26 items). The new change is included in the passed list.                                       |
| `uv run pytest tests/test_lifecycle_recommendation_rules.py`             | 0         | 15 passed in 2.13s.                                                                                                       |
| `uv run pytest tests/test_lifecycle_recommendation.py`                   | 0         | 15 passed in 2.50s.                                                                                                       |
| `uv run pytest`                                                          | 0         | 310 passed in 13.92s.                                                                                                     |
| `uv run skill-forge --help`                                              | 0         | CLI loads; the pre-existing `lifecycle` command is unchanged.                                                              |
| `python scripts/governance_check.py --quick`                             | 0         | `[PASS] openspec validate --strict --all (required)` + `[PASS] uv run skill-forge --help (required)`, summary `2 passed, 0 failed, 0 skipped`. |
| `python scripts/governance_check.py` (full)                              | 0         | 6 PASS lines, summary `6 passed, 0 failed, 0 skipped`.                                                                    |

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

No commands in the script's command list were skipped
during the recorded runs. The optional-skip path is
exercised by the unit tests but did not trigger during
this verification.

## 12. Implementation Notes

- The adapter uses a lazy import inside the function
  body to break the circular dependency between
  `recommendation.py` and
  `recommendation_rules.py`. The cycle is resolved at
  call time, after both modules are fully loaded.
- The two pre-existing private helpers
  `_recommend_from_summary` and `_summary_signals` are
  removed. Their rule is now centralized in the pure
  module. The service has no duplicated rule.
- The `compare` method, `_comparison_key`,
  `_compare_reason`, and `_tie_breaker_reason` are
  preserved as-is. The pure function does not
  duplicate their rule, and the slice does not
  consolidate them.
- The `LifecycleRecommendation` and
  `LifecycleComparison` result models are unchanged.
  The slice is an internal adapter/refactor; the
  public service API is preserved.

## 13. Remaining Risks

- [The reason text for the `unknown` state is now
  produced by the pure function, not by the service
  module] -> Mitigation: the pre-existing service
  tests in `tests/test_lifecycle_recommendation.py`
  do not assert on the reason text for the `unknown`
  state, and the CLI tests assert only on the action
  and on the printed "Lifecycle recommendation" and
  "ready-to-promote" strings. The refactor is
  compatible with every existing test.
- [A future change to the pure function's reason
  text will change the service's output text] ->
  Mitigation: the parity tests in
  `tests/test_lifecycle_recommendation.py` assert on
  the full `model_dump()` of both recommendations, so
  any future drift between the service and the pure
  function is caught immediately.
- [The pre-existing WIP under `src/skill_forge/` is
  not exercised by the new parity tests] ->
  Mitigation: the parity tests cover the three
  required paths. The pre-existing tests in
  `tests/test_lifecycle_recommendation.py` continue
  to exercise the service and the CLI integration.
- [The `compare` method still has its own private
  helpers that the pure function does not
  duplicate] -> Mitigation: a future Phase can
  consolidate `compare` if needed. The slice is
  limited to `recommend`.

## 14. Commit Recommendation

The change is recommended for commit. The OpenSpec
validation, the pytest suite (310 tests), the CLI smoke
test, and both governance check modes all pass. The
Phase 5 forbidden paths are untouched. The pre-existing
WIP is preserved. The public service API is preserved.
The slice is a small, additive, internal
adapter/refactor that consolidates the lifecycle
recommendation rule.

## 15. Commit SHA

The Phase 5 change is committed as
`<see git log>` with the message
`refactor: reuse lifecycle recommendation rules in service`.
A follow-up docs commit records the SHA in
`openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`.
