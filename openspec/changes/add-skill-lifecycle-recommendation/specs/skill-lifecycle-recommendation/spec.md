# Skill Lifecycle Recommendation Specification

> Status: draft
> Schema: skill-forge-governance
> Capability: `skill-lifecycle-recommendation`
> File: `specs/skill-lifecycle-recommendation/spec.md`
>
> This spec describes the minimal, deterministic, testable
> slice of the lifecycle recommendation capability. The slice
> adds the pure function `recommend_lifecycle_action` and the
> `LifecycleRecommendationInput` model. CLI integration, the
> compare view, and persistence are out of scope and will be
> added by later phases.

## Purpose

Provide a deterministic, in-memory, file-free mapping from a
structured set of lifecycle facts to a single
`LifecycleRecommendation` result. The mapping is a pure
function that is the testable anchor for the broader
lifecycle recommendation feature.

## ADDED Requirements

### Requirement: Lifecycle recommendation input model

The system SHALL provide a `LifecycleRecommendationInput`
Pydantic model that captures the structured facts required to
derive a lifecycle recommendation.

#### Scenario: Input model accepts the full fact set

- **WHEN** a caller constructs a `LifecycleRecommendationInput`
  with `skill_name`, `state`, `reason`, `missing_facts`,
  `quality_score`, `quality_status`, `eval_total`,
  `eval_passed`, `eval_failed`, and
  `applied_experience_rule_ids`
- **THEN** construction succeeds
- **AND** the model exposes all of the supplied fields
- **AND** unknown fields are rejected

#### Scenario: Input model rejects an empty skill name

- **WHEN** a caller constructs a `LifecycleRecommendationInput`
  with `skill_name` equal to `""`
- **THEN** construction fails with a `ValidationError`

#### Scenario: Input model rejects an unknown state

- **WHEN** a caller constructs a `LifecycleRecommendationInput`
  with `state` equal to a value outside the `LifecycleState`
  literal (`healthy`, `needs-eval`, `needs-upgrade`,
  `regressed`, `unknown`)
- **THEN** construction fails with a `ValidationError`

#### Scenario: Input model rejects unknown fields

- **WHEN** a caller constructs a `LifecycleRecommendationInput`
  with a field that is not in the model's schema
- **THEN** construction fails with a `ValidationError`

### Requirement: Pure recommendation function

The system SHALL provide a `recommend_lifecycle_action`
function that maps a `LifecycleRecommendationInput` to a
`LifecycleRecommendation` deterministically, without reading
or writing any file and without invoking any external
service.

#### Scenario: Unknown state recommends investigating missing facts

- **WHEN** `recommend_lifecycle_action` is called with an
  input whose `state` is `"unknown"`
- **THEN** the returned `LifecycleRecommendation.action` is
  `"investigate-missing-facts"`
- **AND** the returned `LifecycleRecommendation.state` is
  `"unknown"`
- **AND** the returned `LifecycleRecommendation.reason`
  mentions that the lifecycle state is unknown

#### Scenario: Outdated provenance recommends investigating missing facts

- **WHEN** `recommend_lifecycle_action` is called with an
  input whose `state` is `"unknown"` and whose
  `missing_facts` includes `"provenance"`
- **THEN** the returned `LifecycleRecommendation.action` is
  `"investigate-missing-facts"`
- **AND** the returned `LifecycleRecommendation.missing_facts`
  contains `"provenance"`

#### Scenario: Needs-eval state recommends running evaluation

- **WHEN** `recommend_lifecycle_action` is called with an
  input whose `state` is `"needs-eval"`
- **THEN** the returned `LifecycleRecommendation.action` is
  `"run-eval"`
- **AND** the returned `LifecycleRecommendation.state` is
  `"needs-eval"`

#### Scenario: Regressed state recommends repairing regression

- **WHEN** `recommend_lifecycle_action` is called with an
  input whose `state` is `"regressed"`
- **THEN** the returned `LifecycleRecommendation.action` is
  `"repair-regression"`
- **AND** the returned `LifecycleRecommendation.state` is
  `"regressed"`

#### Scenario: Needs-upgrade state recommends considering an upgrade

- **WHEN** `recommend_lifecycle_action` is called with an
  input whose `state` is `"needs-upgrade"`
- **THEN** the returned `LifecycleRecommendation.action` is
  `"consider-upgrade"`
- **AND** the returned `LifecycleRecommendation.state` is
  `"needs-upgrade"`

#### Scenario: Healthy state recommends readiness to promote

- **WHEN** `recommend_lifecycle_action` is called with an
  input whose `state` is `"healthy"`, `quality_score` is
  greater than or equal to `90`, `quality_status` is
  `"valid"`, `eval_total` is greater than `0`, and
  `eval_failed` is `0`
- **THEN** the returned `LifecycleRecommendation.action` is
  `"ready-to-promote"`
- **AND** the returned `LifecycleRecommendation.state` is
  `"healthy"`
- **AND** the returned `LifecycleRecommendation.reason`
  mentions that the package is healthy
- **AND** the returned `LifecycleRecommendation.missing_facts`
  is empty

#### Scenario: Function is deterministic on repeated calls

- **WHEN** `recommend_lifecycle_action` is called multiple
  times with the same input
- **THEN** each call returns a `LifecycleRecommendation`
  whose serialized form is equal to the others
- **AND** the input is not mutated by any call

## MODIFIED Requirements

None. The pre-existing service-level requirements in
`openspec/specs/skill-lifecycle-recommendation/` are out of
scope for this slice. They will be re-evaluated when a future
phase reshapes the service to use the pure function.

## REMOVED Requirements

### Requirement: (none)

This capability does not remove any existing requirement.

## RENAMED Requirements

### Requirement: (none)

This capability does not rename any existing requirement.
