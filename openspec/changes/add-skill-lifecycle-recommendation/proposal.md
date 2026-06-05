# Proposal: add-skill-lifecycle-recommendation

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 3 (first governed change slice)
> Date: 2026-06-06
>
> This is the minimal, deterministic, testable slice of the
> lifecycle recommendation change. CLI integration, persistence,
> and a wider compare surface are intentionally out of scope.
> The pre-existing WIP (service, CLI commands, integration tests)
> is preserved as-is and is not modified by this slice.

## Why

Skill Forge exposes a read-only lifecycle index, but the user has
to interpret the summary and pick a next action manually. A pure,
deterministic recommendation function turns a structured set of
lifecycle facts into a concrete next best action with a stable
reason, without requiring LLM calls, file I/O, or a clock. The
function is the minimal anchor that the rest of the lifecycle
recommendation feature can build on in later phases.

This is the first code-bearing change run end-to-end under the
new `skill-forge-governance` eight-artifact schema. It must be
small enough that the artifacts, the code, and the tests can be
reviewed in a single session.

## What Changes

- Add a new module `src/skill_forge/lifecycle/recommendation_rules.py`
  with a `LifecycleRecommendationInput` Pydantic model and a pure
  `recommend_lifecycle_action(input) -> LifecycleRecommendation`
  function.
- Add a new test file `tests/test_lifecycle_recommendation_rules.py`
  with unit tests for the pure function. The tests cover at least:
  new or unknown skill state, outdated provenance, current valid
  metadata, invalid or incomplete input, and deterministic behavior.
- Re-shape the existing four OpenSpec artifacts in this change
  folder to fit the new schema, and add the four missing artifacts
  (`brainstorm.md`, `review.md`, `plan.md`, `verification.md`).
- Update `.openspec.yaml` so the change declares
  `schema: skill-forge-governance` and validates under
  `openspec validate add-skill-lifecycle-recommendation --strict`.

## Capabilities

### New Capabilities

- `skill-lifecycle-recommendation`: deterministic next best action
  derived from a structured `LifecycleRecommendationInput` fact
  set. The Phase 3 slice adds only the pure function and its input
  model. CLI commands, the comparison view, and persistence are
  out of scope and will be added by later phases.

### Modified Capabilities

- None. No existing capability's requirements are changed by
  this slice.

### Removed Capabilities

- None.

## Impact

- Code: a new module `src/skill_forge/lifecycle/recommendation_rules.py`.
  No existing module under `src/skill_forge/lifecycle/` is modified.
- CLI: none. CLI integration is explicitly out of scope for this
  slice.
- Schemas: none. No stored artifact schema changes
  (`skill-forge.json`, `eval-report.json`, `config.yaml`,
  blueprint schema are all unchanged).
- Workspaces: none. The pure function does not read or write
  any workspace file.
- Dependencies: none. `pyproject.toml` and `uv.lock` are not
  modified.
- OpenSpec tree: this change folder is reshaped from the old
  four-artifact structure to the new eight-artifact structure
  required by the `skill-forge-governance` schema.

## Non-Goals

- CLI integration (`skill-forge lifecycle recommend ...` and
  `skill-forge lifecycle compare ...`). The CLI surface is
  pre-existing WIP and is not modified by this slice.
- Persistence. The pure function does not write to disk.
- Templates. No template under `templates/` is modified.
- Dependencies. No new third-party dependency is added.
- The lifecycle compare view. Compare is a sibling read-only
  command and is not part of the minimal deterministic slice.
- Adaptation of the existing `LifecycleRecommendationService` to
  use the new pure function. That adapter is a separate
  follow-up change.

## Risks

- [Action vocabulary drift between the new pure function and the
  pre-existing service] -> Mitigation: the pure function uses the
  same five action labels and the same `LifecycleState` literal
  that the service uses. Any future divergence is caught by a
  comparison test in a later phase.
- [The pure function's state-mapping rule is duplicated between
  the new module and the existing service] -> Mitigation: the
  new module is additive. A future consolidation change can
  refactor the service to call the pure function without
  changing the public API. That refactor is out of scope here.
- [The new test file does not exercise the pre-existing service
  and may leave a gap if the service diverges] -> Mitigation:
  the pre-existing `tests/test_lifecycle_recommendation.py`
  continues to exercise the service and is preserved as-is.
  Future phases can add a parity test.

## Rollback

1. Delete the file `src/skill_forge/lifecycle/recommendation_rules.py`.
2. Delete the file `tests/test_lifecycle_recommendation_rules.py`.
3. Restore the original `openspec/changes/add-skill-lifecycle-recommendation/.openspec.yaml`
   to `schema: spec-driven` (the value it had before this slice).
4. Revert the four reshaped OpenSpec artifacts
   (`proposal.md`, `design.md`, `tasks.md`,
   `specs/skill-lifecycle-recommendation/spec.md`) to their
   pre-Phase-3 content.
5. Remove the four new artifacts
   (`brainstorm.md`, `review.md`, `plan.md`, `verification.md`).
6. No data migration is required: the pure function did not
   write to disk.

## Consistency With Brainstorm

- Brainstorm file: `brainstorm.md` (in this folder).
- Recommended option: Option A (pure function module under
  `src/skill_forge/lifecycle/recommendation_rules.py`).
- Deviations and reasons: none. The proposal implements Option A
  exactly as the brainstorm describes it.
