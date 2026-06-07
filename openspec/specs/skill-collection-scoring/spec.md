# skill-collection-scoring Specification

## Purpose
TBD - created by archiving change add-skill-collection-governance. Update Purpose after archive.
## Requirements
### Requirement: Collection scoring is deterministic
The system SHALL derive collection scoring from local deterministic
signals rather than subjective hidden heuristics.

#### Scenario: Same evidence yields same score
- **WHEN** the same local evidence set is processed more than once
- **THEN** the system SHALL produce the same score outputs

#### Scenario: Missing signals are allowed
- **WHEN** one or more evidence signals are missing
- **THEN** the system SHALL still produce a score result and SHALL treat
  missing evidence conservatively

### Requirement: Scoring combines existing local quality signals
The system SHALL compute collection and promotion scores from existing
local evidence dimensions.

#### Scenario: Validation and quality affect score
- **WHEN** a Skill has stronger validation and content quality signals
- **THEN** the score SHALL rank it above a similar Skill with weaker
  structural or quality signals

#### Scenario: Eval affects score
- **WHEN** one Skill has passing eval evidence and another has repeated
  eval failures
- **THEN** the passing Skill SHALL receive a stronger promotion score

#### Scenario: Lifecycle affects score
- **WHEN** lifecycle evidence indicates a healthier or more reusable
  Skill state
- **THEN** that signal SHALL contribute positively to score output

### Requirement: Scoring is explainable
The system SHALL preserve score dimensions and evidence references so
users can inspect why a Skill was curated or promoted.

#### Scenario: Score explanation shows dimensions
- **WHEN** a user inspects a collection score
- **THEN** the system SHALL display or persist dimension-level evidence
  such as validation, quality, eval, lifecycle, provenance, or reuse

#### Scenario: Score model is versioned
- **WHEN** the score formula changes
- **THEN** the system SHALL record a score model version or equivalent
  metadata with stored score snapshots
