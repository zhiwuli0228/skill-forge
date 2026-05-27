## ADDED Requirements

### Requirement: Search can explain ranking scores
The system SHALL provide an optional search explanation mode that displays deterministic score components for each returned result.

#### Scenario: Explain search scores
- **WHEN** a user runs `skill-forge search "<query>" --explain`
- **THEN** each displayed result SHALL include relevance, authority, completeness, freshness, platform boost, and final score values

#### Scenario: Default search remains compact
- **WHEN** a user runs `skill-forge search "<query>"` without `--explain`
- **THEN** the command SHALL display the normal compact search result table without score component explanation columns

### Requirement: Search explanation reflects existing ranking components
The system SHALL use the same ranking component values already used to calculate returned search scores.

#### Scenario: Platform boost is visible
- **WHEN** a user runs search with both `--platform <platform>` and `--explain`
- **THEN** results matching the requested platform SHALL display a positive platform boost

#### Scenario: Freshness boost is visible
- **WHEN** a returned result has a freshness boost from recent corpus metadata and `--explain` is enabled
- **THEN** the output SHALL display that freshness boost value
