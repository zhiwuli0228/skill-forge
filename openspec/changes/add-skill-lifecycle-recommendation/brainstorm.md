# Brainstorm: add-skill-lifecycle-recommendation

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 3 (first governed change slice)
> Date: 2026-06-06
>
> Brainstorm is the first artifact. It is required because the change
> introduces a new lifecycle recommendation capability under the
> `skill-forge-governance` schema, and the eight-artifact flow
> mandates a brainstorm for new capabilities.

## Problem

Skill Forge exposes a read-only lifecycle index (`LifecycleSummary`),
but the user has to interpret the summary and decide the next action
manually. A deterministic recommendation layer turns that summary into
a concrete next step without adding LLM dependence or file mutation.
The existing WIP already has a service-level recommendation that
reads from disk; what is missing is a pure, testable, deterministic
recommendation function that can be used in isolation and is
trivially unit-testable.

How do we add a pure recommendation function — no I/O, no clock, no
persistence — that the rest of the project can build on later?

## Context

- `src/skill_forge/lifecycle/models.py` defines `LifecycleSummary` and the
  `LifecycleState` literal (healthy, needs-eval, needs-upgrade,
  regressed, unknown). The recommendation action vocabulary is
  already defined in `src/skill_forge/lifecycle/recommendation.py`:
  `investigate-missing-facts`, `run-eval`, `repair-regression`,
  `consider-upgrade`, `ready-to-promote`.
- `src/skill_forge/lifecycle/recommendation.py` already implements a
  `LifecycleRecommendationService` that consumes a `LifecycleSummary`
  and produces a `LifecycleRecommendation`. The service depends on
  `LifecycleService`, which reads `skill-forge.json` and
  `eval-report.json` from disk. The service is pre-existing WIP and
  is not part of this Phase 3 slice.
- `tests/test_lifecycle_recommendation.py` already exercises the
  service-level recommendation and CLI integration. Those tests are
  pre-existing WIP and are not modified by this slice.
- The project rule (AGENTS.md Section 5) is strict-scope. This phase
  may only touch `openspec/changes/add-skill-lifecycle-recommendation/**`,
  `src/skill_forge/lifecycle/**`, `tests/**`, and
  `docs/00-project/first-governed-change-verification-report.md`.
- The new schema `skill-forge-governance` (Phase 1) requires eight
  artifacts: `brainstorm`, `proposal`, `spec`, `design`, `review`,
  `plan`, `tasks`, `verification`. The change folder currently has
  four of them under the old `spec-driven` schema.

## Options

### Option A: A pure function module under `src/skill_forge/lifecycle/`

- **Changes**: add `src/skill_forge/lifecycle/recommendation_rules.py`
  with a new `LifecycleRecommendationInput` Pydantic model and a pure
  `recommend_lifecycle_action(input) -> LifecycleRecommendation`
  function. Add `tests/test_lifecycle_recommendation_rules.py` with
  unit tests for the pure function.
- **Does not change**: the existing `LifecycleRecommendationService`,
  the existing CLI integration, the existing recommendation tests,
  templates, dependencies, or any other lifecycle module.
- **Top risk**: the pure function duplicates state-based logic that
  is already in the service-level `_recommend_from_summary`. A
  future refactor may want to consolidate them.
- **Effort**: small (one new module, one new test file, eight
  OpenSpec artifacts).

### Option B: Replace `_recommend_from_summary` in the existing service

- **Changes**: rewrite the existing `LifecycleRecommendationService`
  so that its internal recommendation logic is exposed as a pure
  function. Tests for the service remain; no new module is added.
- **Does not change**: the service API surface, the CLI integration.
- **Top risk**: this slice touches pre-existing WIP (the existing
  service). The Phase 3 strict-scope rule explicitly forbids
  touching unrelated WIP. Verdict: violates the scope rule.
- **Effort**: medium (one module edit, one test edit).

### Option C: Add the pure function as a static method on a new class

- **Changes**: define a `LifecycleRecommendationRules` class with a
  static `recommend(input) -> LifecycleRecommendation` method.
- **Does not change**: the existing service.
- **Top risk**: a static-method class is a heavier abstraction than
  the rule needs. The task says "pure recommendation function" —
  a module-level function is the simpler shape.
- **Effort**: small (one new module, one new test file).

## Assumptions

- [verified] The action vocabulary in `recommendation.py` is stable
  and is the right starting point for the pure function.
- [verified] The `LifecycleState` literal covers all states the
  pure function must handle.
- [verified] The existing `LifecycleRecommendation` result model
  carries enough information for the pure function to return a
  stable, explainable result.
- [unverified] The pre-existing WIP (service, CLI, integration
  tests) is preserved as-is. Phase 3 must not silently consume
  the WIP. Mitigation: the new module and test file are added
  alongside, not in place of, the existing code.
- [unverified] Future phases will adapt `LifecycleSummary` into
  `LifecycleRecommendationInput` at the service boundary. That
  adapter is out of scope for Phase 3.

## Open Questions

- [non-blocking] Should the pure function live in
  `recommendation_rules.py` (separate module) or in `recommendation.py`
  (alongside the service)? Resolved below.
- [non-blocking] Should the result model be a new
  `LifecycleRecommendationResult` or reuse the existing
  `LifecycleRecommendation`? Resolved below.
- [blocking, resolved] Does the slice need to add the four missing
  OpenSpec artifacts (`brainstorm`, `review`, `plan`, `verification`)
  to satisfy the new schema? Yes, otherwise the change cannot
  pass `openspec validate --strict --all`.

## Recommendation

- Recommended: **Option A** (a pure function module under
  `src/skill_forge/lifecycle/recommendation_rules.py`).
- Reason: it is the smallest diff that satisfies the task. The new
  module and test file are additive; the existing WIP is preserved.
  The pure function is trivially testable and is the deterministic
  anchor that the next phase's compare logic can reuse.
