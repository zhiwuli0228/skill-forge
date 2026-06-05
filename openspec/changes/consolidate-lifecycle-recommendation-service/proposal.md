# Proposal: consolidate-lifecycle-recommendation-service

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 5 (lifecycle recommendation service adapter)
> Date: 2026-06-06
>
> This is an internal adapter/refactor slice. It does not
> change user-facing behavior, does not add CLI commands,
> does not add persistence, does not add dependencies, and
> does not touch pre-existing WIP.

## Why

The Phase 3 change added a pure, deterministic
`recommend_lifecycle_action` function. The pre-existing
service-level recommendation code has a state-based rule
that duplicates the pure function's rule. The two rules
must stay in sync manually; a future state-mapping change
to the pure function will silently leave the service-level
rule behind. The Phase 3 verification report lists this
rule duplication as the top "remaining risk".

Phase 5 consolidates the rule by making the
service-level `recommend` method call the pure function
through a small adapter. The public service API is
preserved; the CLI surface is preserved; no dependencies
are added.

## What Changes

- Add a private adapter `_summary_to_input` in
  `src/skill_forge/lifecycle/recommendation.py` that
  constructs a `LifecycleRecommendationInput` from the
  fields of a `LifecycleSummary`.
- Modify `LifecycleRecommendationService.recommend` to
  call `recommend_lifecycle_action(_summary_to_input(summary))`.
- Remove the now-redundant `_recommend_from_summary` and
  `_summary_signals` private functions from
  `src/skill_forge/lifecycle/recommendation.py`.
- Keep the `compare` method, `_comparison_key`,
  `_compare_reason`, and `_tie_breaker_reason` private
  helpers in `recommendation.py` as-is; they are not
  duplicated by the pure function and are out of scope
  for this slice.
- Add parity tests to
  `tests/test_lifecycle_recommendation.py` that verify
  the service-level `recommend` method matches the
  pure function for the same `LifecycleState` across
  three paths: outdated provenance, current metadata,
  unknown/new skill.
- Add a new change folder
  `openspec/changes/consolidate-lifecycle-recommendation-service/`
  with the full eight OpenSpec artifacts.
- Add a new verification report
  `docs/00-project/lifecycle-service-adapter-verification-report.md`.

## Capabilities

### New Capabilities

- `lifecycle-recommendation-service-adapter`: a private
  adapter inside
  `src/skill_forge/lifecycle/recommendation.py` that
  bridges `LifecycleSummary` (a service-level data
  carrier) and `LifecycleRecommendationInput` (the
  pure function's input model). The adapter is private
  to the lifecycle sub-package and is not part of the
  public CLI surface.

### Modified Capabilities

- None. No existing capability's requirements are
  changed by this slice.

### Removed Capabilities

- None.

## Impact

- Code: one private adapter function in
  `src/skill_forge/lifecycle/recommendation.py`. One
  refactored `recommend` method. Two private functions
  removed. No other file under `src/skill_forge/` is
  modified.
- CLI: none. `uv run skill-forge --help` output is
  unchanged. The pre-existing
  `skill-forge lifecycle recommend` and
  `skill-forge lifecycle compare` commands are
  preserved.
- Schemas: none. `skill-forge.json`, `eval-report.json`,
  `config.yaml`, blueprint schema, and the
  `LifecycleRecommendation` result model are
  unchanged.
- Workspaces: none. The service does not write to any
  workspace file.
- Dependencies: none. `pyproject.toml` and `uv.lock`
  are not modified.
- Tests: parity tests added to
  `tests/test_lifecycle_recommendation.py`. The
  pre-existing tests in
  `tests/test_lifecycle_recommendation.py` and
  `tests/test_lifecycle_recommendation_rules.py`
  remain valid; the slice does not modify their
  expected behavior.
- OpenSpec tree: one new change folder is added under
  `openspec/changes/consolidate-lifecycle-recommendation-service/`.
  The change uses the `skill-forge-governance` schema.

## Non-Goals

- CLI integration changes. `src/skill_forge/cli.py` is
  out of scope; the CLI surface is preserved.
- Persistence. The adapter does not write to disk.
- Templates. No template under `templates/` is
  modified.
- Dependencies. No new third-party dependency is
  added.
- The lifecycle compare view. The `compare` method
  has its own private helpers; consolidating them is
  out of scope for this slice.
- The pre-existing WIP. Files under
  `src/skill_forge/lifecycle/__init__.py`,
  `src/skill_forge/lifecycle/models.py`,
  `src/skill_forge/lifecycle/service.py`, and
  `src/skill_forge/lifecycle/promotion.py` are not
  modified.

## Risks

- [A circular import between `recommendation.py` and
  `recommendation_rules.py`] -> Mitigation: the adapter
  uses a lazy import inside the private function, so
  the circular import is resolved at call time, not at
  module load time.
- [A future Phase changes the pure function's reason
  text, and the service's output text changes] ->
  Mitigation: the existing service-level tests do not
  assert on the reason text for the `unknown` state,
  and the CLI tests assert only on the action and on
  the printed "Lifecycle recommendation" and
  "ready-to-promote" strings. The refactor is
  compatible with every existing test.
- [The adapter drops a field that the service used to
  pass to its private rule] -> Mitigation: the
  adapter passes every field of
  `LifecycleRecommendationInput` that the service
  needs. The fields are listed in
  `design.md` and verified by the parity tests.
- [The pre-existing WIP under `src/skill_forge/` is
  not exercised by the new parity tests] ->
  Mitigation: the parity tests cover the three
  required paths (outdated provenance, current
  metadata, unknown/new skill). The pre-existing
  tests in `tests/test_lifecycle_recommendation.py`
  continue to exercise the service and the CLI
  integration.

## Rollback

1. Restore
   `src/skill_forge/lifecycle/recommendation.py` to
   its pre-Phase-5 content (the version with
   `_recommend_from_summary` and `_summary_signals`).
2. Delete the new parity tests from
   `tests/test_lifecycle_recommendation.py`.
3. Delete the folder
   `openspec/changes/consolidate-lifecycle-recommendation-service/`.
4. Delete
   `docs/00-project/lifecycle-service-adapter-verification-report.md`.
5. No data migration. The adapter is in-memory only
   and did not write to disk.

## Consistency With Brainstorm

- Brainstorm file: `brainstorm.md` (in this folder).
- Recommended option: Option A (an adapter that builds
  `LifecycleRecommendationInput` from
  `LifecycleSummary` and calls the pure function).
- Deviations and reasons: none. The proposal
  implements Option A exactly as the brainstorm
  describes it.
