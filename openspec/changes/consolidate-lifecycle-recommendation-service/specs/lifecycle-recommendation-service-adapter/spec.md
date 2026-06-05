# Lifecycle Recommendation Service Adapter Specification

> Status: draft
> Schema: skill-forge-governance
> Capability: `lifecycle-recommendation-service-adapter`
> File: `specs/lifecycle-recommendation-service-adapter/spec.md`
>
> This spec describes the internal adapter that bridges
> `LifecycleSummary` (the service-level data carrier) and
> `LifecycleRecommendationInput` (the pure function's
> input model). The slice is an internal
> adapter/refactor; user-facing behavior is preserved.

## Purpose

Centralize the state-based lifecycle recommendation rule
in a single deterministic pure function by making the
service-level `LifecycleRecommendationService.recommend`
method call the Phase 3 pure function
`recommend_lifecycle_action` through a private adapter.
The adapter is a field-by-field mapping from
`LifecycleSummary` to `LifecycleRecommendationInput`.

## ADDED Requirements

### Requirement: Service recommendation delegates to the pure function

The system SHALL make
`LifecycleRecommendationService.recommend(skill_name)`
call the pure function `recommend_lifecycle_action`
through a private adapter that converts the
`LifecycleSummary` produced by `LifecycleService.show`
to a `LifecycleRecommendationInput`.

#### Scenario: Service recommend uses the pure function

- **WHEN** a caller invokes
  `LifecycleRecommendationService.recommend("alpha-skill")`
- **THEN** the service reads a `LifecycleSummary` from
  `LifecycleService.show`
- **AND** the service constructs a
  `LifecycleRecommendationInput` from the summary's
  fields via the private adapter
- **AND** the service calls
  `recommend_lifecycle_action(input)` and returns the
  resulting `LifecycleRecommendation`

#### Scenario: Adapter covers every required field

- **WHEN** the private adapter maps a
  `LifecycleSummary` to a
  `LifecycleRecommendationInput`
- **THEN** the adapter passes `skill_name`, `state`,
  `reason`, `missing_facts`, `quality_score`,
  `quality_status`, `eval_total`, `eval_passed`,
  `eval_failed`, and `applied_experience_rule_ids`

### Requirement: Adapter is the only path from summary to recommendation

The system SHALL ensure that
`LifecycleRecommendationService.recommend` does not
implement its own state-based rule. The service SHALL
delegate to the pure function for the
`action`, `reason`, and `signals` fields.

#### Scenario: Service has no duplicated rule

- **WHEN** a reviewer reads
  `src/skill_forge/lifecycle/recommendation.py`
- **THEN** the file does not contain a private
  function that maps a `LifecycleSummary.state` to a
  `LifecycleRecommendationAction` directly
- **AND** the only path from `LifecycleSummary` to
  `LifecycleRecommendation` is through the pure
  function

### Requirement: Public service API is preserved

The system SHALL preserve the public API of
`LifecycleRecommendationService`. The slice SHALL NOT
change the constructor signature, the public method
signatures, or the result model field set.

#### Scenario: Public methods remain importable

- **WHEN** a caller imports
  `LifecycleRecommendationService` from
  `skill_forge.lifecycle.recommendation`
- **THEN** the import succeeds
- **AND** `LifecycleRecommendationService.__init__`
  accepts a `LifecycleService`
- **AND** `LifecycleRecommendationService.recommend`
  accepts a `skill_name` and returns a
  `LifecycleRecommendation`
- **AND** `LifecycleRecommendationService.compare`
  accepts two skill names and returns a
  `LifecycleComparison`

#### Scenario: Result model is unchanged

- **WHEN** a caller reads
  `LifecycleRecommendation.model_fields`
- **THEN** the field set is `skill_name`, `state`,
  `action`, `reason`, `missing_facts`, `signals`
- **AND** the field types are unchanged

### Requirement: CLI surface is preserved

The system SHALL preserve the CLI surface. The
`skill-forge lifecycle recommend` and
`skill-forge lifecycle compare` commands SHALL produce
the same output for the same input as before the
slice.

#### Scenario: CLI help is unchanged

- **WHEN** a user runs
  `uv run skill-forge lifecycle --help`
- **THEN** the help text is unchanged
- **AND** `uv run skill-forge lifecycle recommend --help`
  and
  `uv run skill-forge lifecycle compare --help`
  show the same flags as before the slice

#### Scenario: CLI recommend output is unchanged

- **WHEN** a user runs
  `uv run skill-forge lifecycle recommend healthy-skill`
  for a Skill whose summary has state `healthy`
- **THEN** the output includes the strings
  `Lifecycle recommendation` and `ready-to-promote`

## MODIFIED Requirements

None. The pre-existing capabilities in
`openspec/specs/skill-lifecycle-recommendation/` are
out of scope for this slice. They will be re-evaluated
when a future change reshapes the `compare` method or
adds new recommendation actions.

## REMOVED Requirements

### Requirement: (none)

This capability does not remove any existing
requirement.

## RENAMED Requirements

### Requirement: (none)

This capability does not rename any existing
requirement.
