## ADDED Requirements

### Requirement: Lifecycle recommendation outputs a deterministic next best action
The system SHALL derive a recommendation for a generated Skill from its lifecycle summary using deterministic rules and a stable action vocabulary.

#### Scenario: Healthy Skill is ready for promotion
- **WHEN** a generated Skill has a healthy lifecycle summary
- **THEN** the system SHALL recommend the next best action using the healthy-state action
- **AND** the recommendation SHALL explain why the Skill is considered ready

#### Scenario: Missing facts produce conservative recommendations
- **WHEN** a generated Skill has missing provenance, eval, quality, or experience facts
- **THEN** the system SHALL choose a conservative recommendation
- **AND** the recommendation SHALL explain which missing facts drove that result

#### Scenario: Same lifecycle summary yields same recommendation
- **WHEN** the same lifecycle summary is evaluated multiple times
- **THEN** the derived recommendation SHALL remain stable
- **AND** the recommendation reason SHALL remain stable

### Requirement: Lifecycle recommendation is exposed through a CLI command
The system SHALL provide a read-only `skill-forge lifecycle recommend <skill-name>` command that displays the recommended next action and the supporting reason.

#### Scenario: Recommend existing generated Skill
- **WHEN** a user runs `skill-forge lifecycle recommend <skill-name>`
- **THEN** the command SHALL display the Skill name
- **AND** the command SHALL display the recommendation action
- **AND** the command SHALL display a deterministic reason string

#### Scenario: Recommend missing generated Skill
- **WHEN** a user runs `skill-forge lifecycle recommend <skill-name>` for a missing generated Skill
- **THEN** the command SHALL exit non-zero with a clear missing generated Skill message

#### Scenario: Recommend command does not mutate files
- **WHEN** a user runs `skill-forge lifecycle recommend <skill-name>`
- **THEN** the command SHALL NOT modify the Skill package
- **AND** the command SHALL NOT modify the experience store

### Requirement: Lifecycle comparison ranks two generated Skills deterministically
The system SHALL provide a read-only `skill-forge lifecycle compare <skill-a> <skill-b>` command that compares two generated Skills and explains which one is currently healthier or better positioned for the next step.

#### Scenario: Compare two generated Skills
- **WHEN** a user runs `skill-forge lifecycle compare <skill-a> <skill-b>`
- **THEN** the command SHALL display both Skill names
- **AND** the command SHALL display which Skill is preferred by the deterministic ranking
- **AND** the command SHALL explain the ranking basis

#### Scenario: Compare identical lifecycle states
- **WHEN** two generated Skills have equivalent lifecycle ordering inputs
- **THEN** the system SHALL use deterministic tie-breakers
- **AND** the output SHALL explain the tie-breaker used

#### Scenario: Compare missing generated Skill
- **WHEN** a user runs `skill-forge lifecycle compare <skill-a> <skill-b>` and either generated Skill is missing
- **THEN** the command SHALL exit non-zero with a clear missing generated Skill message

### Requirement: Lifecycle recommendation remains local and explainable
The system SHALL base lifecycle recommendations only on local lifecycle summaries and SHALL explain the primary factors behind the result.

#### Scenario: Recommendation uses local summary data
- **WHEN** a lifecycle recommendation is generated
- **THEN** the system SHALL use lifecycle summary state, quality, eval, and missing-fact information
- **AND** the system SHALL NOT require network access

#### Scenario: Recommendation reason is stable
- **WHEN** the same local lifecycle facts are processed multiple times
- **THEN** the recommendation reason SHALL remain stable
