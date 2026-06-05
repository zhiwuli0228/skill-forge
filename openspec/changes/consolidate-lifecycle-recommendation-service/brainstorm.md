# Brainstorm: consolidate-lifecycle-recommendation-service

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 5 (lifecycle recommendation service adapter)
> Date: 2026-06-06
>
> Brainstorm is the FIRST artifact for a non-trivial change. It
> is required because this change introduces a new adapter
> layer between the pre-existing service-level recommendation
> code and the Phase 3 pure function, and the eight-artifact
> flow mandates a brainstorm when a new lifecycle phase or
> module boundary is introduced.

## Problem

The Phase 3 change added a pure, deterministic
`recommend_lifecycle_action` function in
`src/skill_forge/lifecycle/recommendation_rules.py`. The
pre-existing service-level recommendation code in
`src/skill_forge/lifecycle/recommendation.py` has a
state-based recommendation rule that duplicates the pure
function's rule. The two rules must stay in sync manually,
and a future state-mapping change to the pure function will
silently leave the service-level rule behind. The Phase 3
verification report lists this rule duplication as an
explicit "remaining risk".

How do we make the service-level recommendation use the
pure function's deterministic rule, without expanding
user-facing behavior, without adding new dependencies, and
without touching pre-existing WIP?

## Context

- `src/skill_forge/lifecycle/recommendation_rules.py`
  defines `LifecycleRecommendationInput` (a structured
  fact set) and `recommend_lifecycle_action(input)`, the
  pure function. The function reads no global state, no
  environment variables, no clock, no file system, no
  network, and mutates nothing.
- `src/skill_forge/lifecycle/recommendation.py` defines
  `LifecycleRecommendationService`, which exposes
  `recommend(skill_name)` and `compare(left, right)`. The
  `recommend` method reads a `LifecycleSummary` from
  `LifecycleService` and dispatches to a private
  `_recommend_from_summary` function that maps state to
  action and reason.
- The state→action mapping in `_recommend_from_summary`
  duplicates the state→action mapping in
  `_recommend_from_facts` (the private function inside the
  pure module). The two functions differ only in the
  reason text for the `unknown` state and in the
  container types.
- The Phase 3 verification report
  (`docs/00-project/first-governed-change-verification-report.md`)
  records this duplication as the top "remaining risk"
  for Phase 3 and recommends a Phase 5 adapter change.
- The Phase 4 governance check script is in place and
  `python scripts/governance_check.py` runs the full
  gate suite.
- The project rule (`AGENTS.md` Section 5) is
  strict-scope. Phase 5 may only touch
  `openspec/changes/consolidate-lifecycle-recommendation-service/**`,
  `src/skill_forge/lifecycle/recommendation.py`,
  `src/skill_forge/lifecycle/recommendation_rules.py`,
  `tests/test_lifecycle_recommendation.py`,
  `tests/test_lifecycle_recommendation_rules.py`, and
  `docs/00-project/lifecycle-service-adapter-verification-report.md`.
- The CLI surface under `src/skill_forge/cli.py` is
  preserved. The Phase 4 task forbade
  `src/skill_forge/cli.py` modifications, and the Phase 5
  allowed-path list also forbids it.

## Options

### Option A: Adapter that builds `LifecycleRecommendationInput` from `LifecycleSummary`

- **Changes**: add a private adapter
  `_summary_to_input(summary)` in
  `src/skill_forge/lifecycle/recommendation.py` that
  constructs a `LifecycleRecommendationInput` from the
  fields of a `LifecycleSummary`. Modify
  `LifecycleRecommendationService.recommend` to call
  `recommend_lifecycle_action(_summary_to_input(summary))`.
  Remove the now-redundant `_recommend_from_summary` and
  `_summary_signals` private functions. Keep the
  `compare` method, `_comparison_key`, `_compare_reason`,
  and `_tie_breaker_reason` as-is; they are not
  duplicated by the pure function and are out of scope
  for this slice.
- **Does not change**: `src/skill_forge/cli.py`, the
  `LifecycleRecommendation` and `LifecycleComparison`
  result models, the `LifecycleService` API, the
  `LifecycleSummary` model, the pre-existing WIP under
  `src/skill_forge/lifecycle/`, the pre-existing WIP
  under `src/skill_forge/`, the dependencies, the
  schema, the config.
- **Top risk**: a circular import between
  `recommendation.py` and `recommendation_rules.py` (the
  pure module already imports `LifecycleRecommendation`
  from `recommendation.py`). Mitigation: use a lazy
  import inside the adapter function or at the bottom
  of `recommendation.py`, after the class definitions.
- **Effort**: small (one adapter function, one
  refactored `recommend` method, two removed private
  functions, parity tests).

### Option B: Move the rule into a class method on `LifecycleRecommendationService`

- **Changes**: add a `LifecycleRecommendationRules`
  class with a static `from_summary` method that maps
  `LifecycleSummary` to `(action, reason, signals)`.
  Have the service call the static method instead of the
  pure function.
- **Does not change**: the public service API.
- **Top risk**: introduces a parallel class hierarchy
  that the pure function does not need. The pure
  function is a module-level function; a static-method
  class is a heavier abstraction than the rule needs.
  The Phase 3 design explicitly rejected a
  static-method class.
- **Effort**: small (one new class, one refactored
  method).

### Option C: Replace the pure function with the service-level rule

- **Changes**: rewrite the pure function so that its
  state→action mapping is taken from the service-level
  rule. Keep the public surface of the pure function.
- **Does not change**: the public pure function API.
- **Top risk**: reverses the Phase 3 design direction.
  The pure function is the deterministic anchor; the
  service is the orchestrator. Pulling the rule back
  into the service defeats the purpose of the pure
  function.
- **Effort**: small (one rule swap).

## Assumptions

- [verified] The pure function's `LifecycleRecommendationInput`
  carries every field the service needs to build a
  recommendation. The fields are: `skill_name`, `state`,
  `reason`, `missing_facts`, `quality_score`,
  `quality_status`, `eval_total`, `eval_passed`,
  `eval_failed`, `applied_experience_rule_ids`. Every
  field has a corresponding field on `LifecycleSummary`,
  so the adapter is field-by-field.
- [verified] The existing service-level tests in
  `tests/test_lifecycle_recommendation.py` do not assert
  on the reason text for the `unknown` state, so the
  reason-text difference between the pure function and
  the service-level rule does not break any test.
- [verified] The CLI tests in
  `tests/test_lifecycle_recommendation.py` assert on
  the `action` field and on the printed `Lifecycle
  recommendation` and `ready-to-promote` strings, not
  on the reason text. The refactor preserves both
  fields.
- [unverified] The pre-existing WIP (service, CLI,
  integration tests) is preserved as-is. Phase 5 must
  not silently consume the WIP. Mitigation: the
  refactor is additive; the only files modified are the
  two allowed source files, the two allowed test files,
  the new OpenSpec change folder, and the new
  verification report.
- [unverified] A future Phase will add additional
  parity tests for the `compare` method. The `compare`
  method is out of scope for this slice.

## Open Questions

- [blocking, resolved] Where should the adapter live?
  Resolved: in `recommendation.py`, as a private
  function `_summary_to_input`. The pure module is the
  deterministic anchor; the service is the orchestrator.
  The adapter belongs in the orchestrator.
- [blocking, resolved] How should the circular import
  between `recommendation.py` and
  `recommendation_rules.py` be handled? Resolved: by
  using a lazy import inside the adapter function, or
  by placing the import at the bottom of
  `recommendation.py` after the class definitions. The
  lazy import is the cleanest pattern.
- [non-blocking] Should the pure function be modified
  to expose a `recommend_from_input(input)` API? No.
  The public function `recommend_lifecycle_action` is
  already the entry point. No new public API is needed.
- [non-blocking] Should the adapter also handle the
  `compare` path? No. The `compare` method has its own
  private helpers (`_comparison_key`,
  `_compare_reason`, `_tie_breaker_reason`) that the
  pure function does not duplicate. A future Phase can
  consolidate `compare` if needed.

## Recommendation

- Recommended: **Option A** (an adapter that builds
  `LifecycleRecommendationInput` from `LifecycleSummary`
  and calls the pure function).
- Reason: it is the smallest diff that satisfies the
  task. The adapter is additive; the only removed code
  is two private functions whose rule is now centralized
  in the pure module. The public service API is
  preserved. The CLI surface is preserved. No new
  dependencies. No new persisted artifacts.
