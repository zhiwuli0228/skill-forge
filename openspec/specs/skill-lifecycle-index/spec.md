# skill-lifecycle-index Specification

## Purpose
Define a read-only lifecycle index for generated Skill packages. This capability aggregates provenance, quality, eval, and experience facts into a single deterministic status view without mutating the Skill package or the local experience store.

## Requirements

### Requirement: Lifecycle index aggregates local Skill facts
The system SHALL derive a lifecycle index for a generated Skill from local provenance, quality, eval, and experience facts without requiring network access.

#### Scenario: Lifecycle index reads local facts
- **WHEN** a user requests a lifecycle summary for a generated Skill
- **THEN** the system SHALL read `skill-forge.json` provenance data when present
- **AND** the system SHALL read `eval-report.json` when present
- **AND** the system SHALL read local experience rule usage data when present
- **AND** the system SHALL use content quality metrics from provenance when available

#### Scenario: Missing facts are allowed
- **WHEN** one or more of provenance, eval, quality, or experience facts are missing
- **THEN** the system SHALL still produce a lifecycle summary
- **AND** it SHALL treat the missing facts as part of the lifecycle state rather than as a failure

### Requirement: Lifecycle summary is exposed through a CLI command
The system SHALL provide a read-only `skill-forge lifecycle show <skill-name>` command that displays the current lifecycle state and the evidence behind it.

#### Scenario: Lifecycle show displays summary
- **WHEN** a user runs `skill-forge lifecycle show <skill-name>`
- **THEN** the command SHALL display the Skill name
- **AND** the command SHALL display a lifecycle state label
- **AND** the command SHALL display evidence summaries derived from provenance, quality, eval, and experience facts when available

#### Scenario: Lifecycle show does not mutate files
- **WHEN** a user runs `skill-forge lifecycle show <skill-name>`
- **THEN** the command SHALL NOT modify the Skill package
- **AND** the command SHALL NOT modify the experience store

### Requirement: Lifecycle state is deterministic and explainable
The system SHALL classify lifecycle state using deterministic rules and SHALL explain the primary reason for the selected state.

#### Scenario: Same facts produce same state
- **WHEN** the same local facts are processed multiple times
- **THEN** the derived lifecycle state SHALL be stable
- **AND** the reason text SHALL be stable

#### Scenario: Low-signal packages get conservative states
- **WHEN** a generated Skill has insufficient provenance, eval, or experience evidence to support a confident healthy state
- **THEN** the system SHALL return a conservative lifecycle state such as `needs-eval` or `unknown`
- **AND** the summary SHALL explain which missing or weak signals led to that result
