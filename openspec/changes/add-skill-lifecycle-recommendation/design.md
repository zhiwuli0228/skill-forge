# Design: add-skill-lifecycle-recommendation

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, specs/skill-lifecycle-recommendation/spec.md
>
> This is the design for the minimal, deterministic, testable
> slice. CLI integration, persistence, and a wider compare
> surface are intentionally out of scope. The pre-existing
> WIP (service, CLI commands, integration tests) is preserved
> as-is and is not modified by this slice.

## Context

Skill Forge already exposes a read-only lifecycle index
(`LifecycleSummary` produced by `LifecycleService`) and a
service-level `LifecycleRecommendationService` that reads from
disk and returns a `LifecycleRecommendation` per Skill. The
service-level code is pre-existing WIP and is not modified by
this slice.

What is missing for the deterministic, testable anchor of the
recommendation feature is a pure function that:

- takes a structured set of lifecycle facts as input (no package
  path, no `LifecycleService` dependency, no file I/O),
- returns a `LifecycleRecommendation` result deterministically
  (the same input always produces the same output),
- is trivially unit-testable (no tmp_path, no fixtures, no
  monkey-patching),
- can be reused later by the service layer as its core rule, and
  by a future compare view as its ranking rule.

The design below is a single new module
`src/skill_forge/lifecycle/recommendation_rules.py` that contains
the input model and the pure function. The function reuses the
existing `LifecycleRecommendation` result model from
`src/skill_forge/lifecycle/recommendation.py` to avoid duplicating
the action vocabulary and field shape.

## Goals / Non-Goals

### Goals

- Define a `LifecycleRecommendationInput` Pydantic model that
  carries only the structured facts needed for a recommendation.
- Define a pure function `recommend_lifecycle_action(input) -> LifecycleRecommendation`
  that maps the input to a deterministic recommendation.
- Cover five test cases at minimum: unknown / new state,
  outdated provenance, current valid metadata, invalid or
  incomplete input, deterministic behavior on repeated calls.
- Preserve the existing WIP (service, CLI, integration tests)
  without modification.

### Non-Goals

- No CLI integration. The pre-existing CLI commands are
  preserved but not extended.
- No persistence. The pure function does not write to disk.
- No new dependency. `pyproject.toml` and `uv.lock` are not
  modified.
- No template change. `templates/` is not modified.
- No modification of the existing
  `LifecycleRecommendationService`. The pure function is
  additive; an adapter that lets the service call the pure
  function is a follow-up change.
- No compare view. Compare is out of scope for this slice.

## Decisions

### Decision 1: A new module `recommendation_rules.py`

- **Decision**: place the input model and the pure function in
  a new module
  `src/skill_forge/lifecycle/recommendation_rules.py`. Do not
  modify the existing `recommendation.py`.
- **Rationale**: keeping the pure function in its own module
  makes the determinism guarantee explicit. The module's name
  advertises that it is rules-only, not service-level. A
  reviewer can read the module in one pass and see the entire
  rule.
- **Alternatives considered**:
  - "Put the pure function in `recommendation.py` next to the
    service" — rejected. The existing `recommendation.py` is
    pre-existing WIP. Phase 3 must not silently consume the WIP.
    A separate module is the additive shape.
  - "Put the pure function in a class with a static method" —
    rejected. A module-level function is the simpler shape
    and matches the task's "pure recommendation function"
    language.

### Decision 2: Reuse the existing `LifecycleRecommendation`

- **Decision**: the pure function returns the existing
  `LifecycleRecommendation` result model from
  `src/skill_forge/lifecycle/recommendation.py`. No new result
  model is introduced.
- **Rationale**: the result model's field set
  (`skill_name`, `state`, `action`, `reason`, `missing_facts`,
  `signals`) already covers what a downstream caller needs.
  Introducing a parallel result model would duplicate the
  shape and create a future adapter burden.
- **Alternatives considered**:
  - "Define a new `LifecycleRecommendationResult` with fewer
    fields" — rejected. The two result models would drift, and
    a downstream caller would have to pick which one to use.
  - "Return a tuple of `(action, reason, signals)`" — rejected.
    A typed return value is easier to test and harder to misuse.

### Decision 3: State-based rule, with a conservative bias

- **Decision**: the rule is keyed on `LifecycleState`. Each
  state maps to exactly one of the five action labels. The
  `unknown` state maps to `investigate-missing-facts` so that
  an unknown Skill is never silently treated as healthy.
- **Rationale**: state-based mapping is the smallest possible
  rule that is still useful. A conservative bias on `unknown`
  matches the existing service-level behavior and keeps the
  rule predictable.
- **Alternatives considered**:
  - "Score-based rule with weighted facts" — rejected. A
    weighted score would be harder to explain and would not
    match the existing service-level state mapping.
  - "Multi-factor rule that consults `missing_facts` first" —
    rejected. A state-based rule is simpler and easier to
    test. `missing_facts` is preserved on the input and on the
    result for the caller's downstream use.

### Decision 4: The function is pure

- **Decision**: the function reads no global state, no
  environment variables, no clock, no file system, no network.
  It allocates only the `LifecycleRecommendation` it returns.
- **Rationale**: purity is the testability contract. A pure
  function has no setup and no teardown. The unit tests do not
  need `tmp_path` and do not need to mock anything.
- **Alternatives considered**:
  - "Accept a `now()` callable so the result can include a
    timestamp" — rejected. A timestamp is not part of the
    recommendation. Adding a `now()` dependency would break
    determinism.
  - "Accept a logger" — rejected. A pure function should not
    log; logging is a side effect.

### Decision 5: Validation lives on the input model

- **Decision**: invalid or incomplete input is rejected by
  Pydantic when `LifecycleRecommendationInput` is constructed.
  The function does not re-validate.
- **Rationale**: validation at construction is the smallest
  place to put it. A `ValidationError` is the documented
  behavior, and tests can assert on it directly with
  `pytest.raises(ValidationError)`.
- **Alternatives considered**:
  - "Validate inside the function and return a sentinel" —
    rejected. A return value that is sometimes a
    `LifecycleRecommendation` and sometimes a sentinel is
    harder to use and harder to test.

## Data Contracts

No stored artifact schema changes. The pure function does not
read or write `skill-forge.json`, `eval-report.json`,
`config.yaml`, blueprint schema, or any other on-disk artifact.

The only data contract introduced is the in-memory
`LifecycleRecommendationInput` Pydantic model. Its shape is:

```yaml
LifecycleRecommendationInput:
  skill_name: str            # non-empty
  state: LifecycleState      # one of: healthy, needs-eval,
                             #         needs-upgrade, regressed, unknown
  reason: str                # default: ""
  missing_facts: list[str]   # default: []
  quality_score: int | None  # default: null
  quality_status: str | None # default: null
  eval_total: int | None     # default: null
  eval_passed: int | None    # default: null
  eval_failed: int | None    # default: null
  applied_experience_rule_ids: list[str]  # default: []
```

The result model is the existing `LifecycleRecommendation` from
`src/skill_forge/lifecycle/recommendation.py`. Its shape is
unchanged by this slice.

## Module Boundaries

### Added

- `src/skill_forge/lifecycle/recommendation_rules.py`:
  input model and pure function. Imports the existing
  `LifecycleRecommendation` result model and the
  `LifecycleState` literal. No new dependency.
- `tests/test_lifecycle_recommendation_rules.py`: unit tests
  for the pure function. Uses only `pytest` and
  `pydantic.ValidationError`. No fixtures, no tmp_path.

### Modified

- None under `src/skill_forge/lifecycle/`. The existing
  `__init__.py`, `models.py`, `service.py`,
  `recommendation.py`, and `promotion.py` are not modified
  by this slice.

### Untouched

- `src/skill_forge/cli.py` and the existing CLI lifecycle
  commands. The pre-existing WIP is preserved.
- `templates/`, `configs/`, `pyproject.toml`, `uv.lock`.
- Every other module under `src/skill_forge/` that is not
  listed in "Added" or "Modified".

## Compatibility Impact

- Claude Code: no effect. The change is internal to a
  lifecycle sub-package.
- Codex: no effect. The change is a pure function; Codex does
  not invoke it directly.
- opencode: no effect. Same as Codex.
- Generated Skill packages: no effect. The pure function does
  not read or write any package file.

## Offline and Deterministic Mode

- Network unavailable: no effect. The pure function does not
  perform network I/O.
- LLM disabled: no effect. The pure function does not invoke
  any LLM.
- LLM enabled but config missing: no effect. Same.

## Security and Filesystem

- Reads: nothing. The pure function is in-memory only.
- Writes: nothing. No file system write.
- Environment variables: none.

## Risks / Trade-offs

- [The pure function's rule duplicates state-mapping logic
  that also lives in the existing
  `LifecycleRecommendationService`] -> Mitigation: the new
  module is additive. A future change can refactor the
  service to call the pure function without changing the
  service's public API. That refactor is out of scope here.
- [The pure function returns a `LifecycleRecommendation` that
  was originally designed for the service-level use case;
  some fields may not be set by the pure path] ->
  Mitigation: the pure path always sets
  `skill_name`, `state`, `action`, `reason`, `missing_facts`,
  and `signals`. The `signals` list is built from the input
  facts and is always present, even when empty.
- [A future change may want the pure function to also emit
  a `LifecycleComparison`] -> Mitigation: the compare view
  is intentionally out of scope. A future change can add a
  sibling pure function in the same module.

## Migration Plan

### Deploy

1. Land the new module
   `src/skill_forge/lifecycle/recommendation_rules.py`.
2. Land the new test file
   `tests/test_lifecycle_recommendation_rules.py`.
3. Land the reshaped OpenSpec artifacts under
   `openspec/changes/add-skill-lifecycle-recommendation/`.
4. Run `openspec validate add-skill-lifecycle-recommendation --strict`
   and `openspec validate --strict --all`.
5. Run `uv run pytest tests/test_lifecycle_recommendation_rules.py`.
6. Run `uv run pytest` for the full suite.

### Rollback

1. Delete the file
   `src/skill_forge/lifecycle/recommendation_rules.py`.
2. Delete the file
   `tests/test_lifecycle_recommendation_rules.py`.
3. Restore the pre-Phase-3 contents of the four reshaped
   OpenSpec artifacts in the change folder and remove the
   four new ones. Restore `.openspec.yaml` to
   `schema: spec-driven`.
4. No data migration. No user-visible state was changed.

## Open Questions

- [non-blocking] Should the pure function also live in the
  `__all__` of `src/skill_forge/lifecycle/__init__.py`? No,
  for this slice. The function is internal; future phases
  may re-export it once the service adapter is in place.
- [non-blocking] Should the input model be a `TypedDict`
  instead of a Pydantic model? No. Pydantic gives
  `extra="forbid"`, `min_length=1`, and `ValidationError`
  for free, which the test cases for invalid or incomplete
  input depend on.
