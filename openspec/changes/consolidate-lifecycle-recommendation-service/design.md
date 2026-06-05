# Design: consolidate-lifecycle-recommendation-service

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, specs/lifecycle-recommendation-service-adapter/spec.md
>
> This is the design for the internal adapter/refactor
> slice. User-facing behavior is preserved. The CLI surface
> is preserved. No new dependencies are added.

## Context

The Phase 3 change added a pure, deterministic
`recommend_lifecycle_action` function in
`src/skill_forge/lifecycle/recommendation_rules.py`. The
pre-existing service-level recommendation code in
`src/skill_forge/lifecycle/recommendation.py` has a
state-based rule that duplicates the pure function's
rule. The duplication is a maintenance hazard: any future
state-mapping change to the pure function would leave
the service-level rule behind.

The design below is a small adapter that bridges
`LifecycleSummary` (the service-level data carrier) and
`LifecycleRecommendationInput` (the pure function's input
model). The adapter is private to the lifecycle
sub-package. The service's `recommend` method delegates
to the pure function via the adapter. The two private
service-level functions whose rule is now centralized in
the pure module (`_recommend_from_summary` and
`_summary_signals`) are removed.

The `compare` method, `_comparison_key`,
`_compare_reason`, and `_tie_breaker_reason` are not
duplicated by the pure function and are out of scope for
this slice.

## Goals / Non-Goals

### Goals

- Define a private adapter `_summary_to_input` in
  `src/skill_forge/lifecycle/recommendation.py` that
  maps `LifecycleSummary` to
  `LifecycleRecommendationInput`.
- Modify `LifecycleRecommendationService.recommend` to
  call the pure function via the adapter.
- Remove the now-redundant `_recommend_from_summary`
  and `_summary_signals` private functions.
- Add parity tests to
  `tests/test_lifecycle_recommendation.py` that verify
  the service-level output matches the pure function's
  output for the same `LifecycleState` across the three
  required paths.
- Preserve the public service API. Preserve the CLI
  surface. Preserve the `compare` method. Preserve
  the pre-existing tests.

### Non-Goals

- No CLI integration changes. `src/skill_forge/cli.py`
  is out of scope; the CLI surface is preserved.
- No persistence. The adapter is in-memory only.
- No new dependency. `pyproject.toml` and `uv.lock`
  are not modified.
- No template change. `templates/` is not modified.
- No modification of the existing
  `LifecycleRecommendationService.compare` method or
  its helpers.
- No modification of the pre-existing WIP under
  `src/skill_forge/lifecycle/`. The pre-existing
  `__init__.py`, `models.py`, `service.py`, and
  `promotion.py` are preserved.
- No schema or config change. `openspec/schemas/**`
  and `openspec/config.yaml` are forbidden by the
  Phase 5 allowed-path list.

## Decisions

### Decision 1: Adapter lives in `recommendation.py` as a private function

- **Decision**: place the adapter in
  `src/skill_forge/lifecycle/recommendation.py` as a
  module-level private function `_summary_to_input`.
  Do not modify `recommendation_rules.py` to accept
  a `LifecycleSummary` directly.
- **Rationale**: the pure module is the deterministic
  anchor. It must not depend on the service-level data
  carrier. Putting the adapter in the service module
  keeps the dependency direction clean: the service
  depends on the pure module, not the other way around.
- **Alternatives considered**:
  - "Add a `from_summary` class method to
    `LifecycleRecommendationInput`" — rejected. The
    pure module must not import from
    `recommendation.py`'s service class.
  - "Add a new module `recommendation_adapter.py`" —
    rejected. A separate module is heavier than the
    change needs; a single private function in
    `recommendation.py` is the smallest diff.

### Decision 2: Lazy import inside the adapter

- **Decision**: the adapter uses a lazy import inside
  the function body for
  `LifecycleRecommendationInput` and
  `recommend_lifecycle_action`. The import is not at
  the top of `recommendation.py`.
- **Rationale**: the pure module
  (`recommendation_rules.py`) imports
  `LifecycleRecommendation` from `recommendation.py`
  at the top of its file. A top-level import in
  `recommendation.py` of the pure module would create
  a circular import that fails at module load time.
  A lazy import inside the adapter resolves the cycle
  at call time, after both modules are fully loaded.
- **Alternatives considered**:
  - "Move the pure module's import to the bottom of
    its own file" — rejected. The pure module's
    design intent is to be import-clean at the top.
  - "Move `LifecycleRecommendation` to a shared
    models module" — rejected. The Phase 5
    allowed-path list forbids modifying
    `src/skill_forge/lifecycle/models.py`.

### Decision 3: Remove the now-redundant private functions

- **Decision**: remove `_recommend_from_summary` and
  `_summary_signals` from `recommendation.py`. Their
  rule is now centralized in the pure module.
- **Rationale**: the whole point of the slice is to
  eliminate the duplicated rule. Leaving the dead
  functions in place would defeat the purpose.
- **Alternatives considered**:
  - "Keep the private functions for backward
    compat" — rejected. They are private
  (`_leading_underscore`); nothing outside the
  module can depend on them.

### Decision 4: Preserve the public service API and the CLI surface

- **Decision**: do not change
  `LifecycleRecommendationService.__init__`,
  `.recommend`, or `.compare`. Do not change
  `LifecycleRecommendation` or `LifecycleComparison`.
  Do not change `src/skill_forge/cli.py`.
- **Rationale**: Phase 5 is an internal
  adapter/refactor slice. The user-facing behavior
  must be preserved.
- **Alternatives considered**:
  - "Add a new public method `recommend_via_rules`"
    — rejected. The slice must not expand
    user-facing behavior.

### Decision 5: Parity tests cover the three required paths

- **Decision**: add three parity tests to
  `tests/test_lifecycle_recommendation.py`:
  - "service outdated provenance path matches pure
    function"
  - "service current metadata path matches pure
    function"
  - "service unknown/new skill path matches pure
    function"
  Each test compares the service's recommendation
  against the pure function's recommendation for the
  same `LifecycleState` and confirms `action`,
  `state`, `reason`, and `missing_facts` match.
- **Rationale**: the Phase 5 task requires the three
  parity tests. The deterministic test for the pure
  function (`test_function_is_deterministic_on_repeated_calls`)
  remains valid and is not modified.
- **Alternatives considered**:
  - "Add a single parity test that covers all three
    paths" — rejected. A single test that bundles
    three assertions is harder to read and harder to
    triage on failure.

## Data Contracts

No stored artifact schema changes. The adapter does not
read or write `skill-forge.json`, `eval-report.json`,
`config.yaml`, blueprint schema, or any other on-disk
artifact.

The only data contract introduced is the in-memory
mapping from `LifecycleSummary` to
`LifecycleRecommendationInput`. The mapping is
field-by-field:

```yaml
LifecycleSummary -> LifecycleRecommendationInput:
  skill_name: skill_name
  state: state
  reason: reason
  missing_facts: missing_facts            # list copy
  quality_score: quality_score
  quality_status: quality_status
  eval_total: eval_total
  eval_passed: eval_passed
  eval_failed: eval_failed
  applied_experience_rule_ids: applied_experience_rule_ids  # list copy
```

`package_path`, `evidence`, and `resolved_experience_rules`
are not passed to the pure function. They are
service-level concerns that the pure function does not
need.

## Module Boundaries

### Added

- `src/skill_forge/lifecycle/recommendation.py`:
  a new private function `_summary_to_input` that maps
  a `LifecycleSummary` to a
  `LifecycleRecommendationInput`. The function uses
  a lazy import to break the circular dependency
  with `recommendation_rules.py`.

### Modified

- `src/skill_forge/lifecycle/recommendation.py`:
  `LifecycleRecommendationService.recommend` is
  refactored to call the pure function via the
  adapter. The two private functions
  `_recommend_from_summary` and `_summary_signals`
  are removed.
- `tests/test_lifecycle_recommendation.py`:
  three parity tests are added.

### Untouched

- `src/skill_forge/cli.py` and the pre-existing CLI
  lifecycle commands.
- `src/skill_forge/lifecycle/__init__.py`,
  `models.py`, `service.py`, and `promotion.py`.
- `templates/`, `configs/`, `pyproject.toml`,
  `uv.lock`.
- `src/skill_forge/lifecycle/recommendation_rules.py`
  is not modified by this slice. The pure function
  is reused as-is.
- `tests/test_lifecycle_recommendation_rules.py`
  is not modified by this slice. The pure function's
  existing tests remain valid.
- Every other module under `src/skill_forge/` that
  is not listed in "Added" or "Modified".

## Compatibility Impact

- Claude Code: no effect. The slice is internal to a
  lifecycle sub-package.
- Codex: no effect. The slice does not change any
  CLI surface.
- opencode: no effect. Same as Codex.
- Generated Skill packages: no effect. The slice
  does not read or write any package file.

## Offline and Deterministic Mode

- Network unavailable: no effect. The adapter is
  in-memory only.
- LLM disabled: no effect. The pure function does
  not invoke any LLM.
- LLM enabled but config missing: no effect. Same.

## Security and Filesystem

- Reads: nothing. The adapter is in-memory only.
- Writes: nothing. No file system write.
- Environment variables: none.

## Risks / Trade-offs

- [A circular import between `recommendation.py` and
  `recommendation_rules.py`] -> Mitigation: the
  adapter uses a lazy import inside the function
  body. The cycle is resolved at call time, after
  both modules are fully loaded.
- [A future Phase changes the pure function's
  reason text, and the service's output text
  changes] -> Mitigation: the existing
  service-level tests do not assert on the reason
  text for the `unknown` state, and the CLI tests
  assert only on the action and on the printed
  "Lifecycle recommendation" and "ready-to-promote"
  strings. The refactor is compatible with every
  existing test.
- [The adapter drops a field that the service
  previously passed to its private rule] ->
  Mitigation: the adapter passes every field of
  `LifecycleRecommendationInput` that the service
  needs. The fields are listed in the data
  contract above and verified by the parity tests.
- [The pre-existing WIP is not exercised by the
  new parity tests] -> Mitigation: the parity
  tests cover the three required paths. The
  pre-existing tests in
  `tests/test_lifecycle_recommendation.py`
  continue to exercise the service and the CLI
  integration.

## Migration Plan

### Deploy

1. Land the refactored
   `src/skill_forge/lifecycle/recommendation.py`.
2. Land the parity tests in
   `tests/test_lifecycle_recommendation.py`.
3. Land the eight OpenSpec artifacts under
   `openspec/changes/consolidate-lifecycle-recommendation-service/`.
4. Run `openspec validate
   consolidate-lifecycle-recommendation-service
   --strict`.
5. Run `openspec validate --strict --all`.
6. Run
   `uv run pytest tests/test_lifecycle_recommendation_rules.py`.
7. Run
   `uv run pytest tests/test_lifecycle_recommendation.py`.
8. Run `uv run pytest` for the full suite.
9. Run `uv run skill-forge --help` for the smoke
   test.
10. Run `python scripts/governance_check.py --quick`.
11. Run `python scripts/governance_check.py` (full
    mode).
12. Land the verification report under
    `docs/00-project/`.

### Rollback

1. Restore
   `src/skill_forge/lifecycle/recommendation.py`
   to its pre-Phase-5 content (the version with
   `_recommend_from_summary` and
   `_summary_signals`).
2. Delete the new parity tests from
   `tests/test_lifecycle_recommendation.py`.
3. Delete the folder
   `openspec/changes/consolidate-lifecycle-recommendation-service/`.
4. Delete
   `docs/00-project/lifecycle-service-adapter-verification-report.md`.
5. No data migration. The adapter is in-memory only
   and did not write to disk.

## Open Questions

- [non-blocking] Should the adapter also handle the
  `compare` path? Resolved: no. The `compare` method
  has its own private helpers that the pure function
  does not duplicate. A future Phase can
  consolidate `compare` if needed.
- [non-blocking] Should the adapter be a method on
  `LifecycleRecommendationService` instead of a
  module-level function? Resolved: no. A
  module-level private function is the smallest
  diff; a method would change the service's public
  surface in a way that is not needed.
- [non-blocking] Should the parity tests also
  assert on the `signals` field? Resolved: yes, the
  tests assert on the full `model_dump()` of both
  recommendations to guarantee byte-for-byte
  parity.
