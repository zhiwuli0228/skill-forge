## ADDED Requirements

### Requirement: Update summary reports full source status
The system SHALL summarize research update outcomes across updated, skipped, failed, and disabled sources.

#### Scenario: Summary includes disabled sources
- **WHEN** a user runs `skill-forge update` and one or more configured sources are disabled
- **THEN** the command SHALL display the disabled source count in the update summary

#### Scenario: Partial update is identified
- **WHEN** a user runs `skill-forge update` and at least one enabled source succeeds while another enabled source fails
- **THEN** the command SHALL identify the update as partial while still exiting successfully

### Requirement: Failed source outcomes include retry guidance
The system SHALL provide deterministic retry guidance for failed research source updates.

#### Scenario: Failed source displays guidance
- **WHEN** a source update fails
- **THEN** the update output SHALL include the failure message and guidance to retry with `skill-forge update` after resolving the source issue

#### Scenario: All sources fail remains non-zero
- **WHEN** all enabled sources fail during update
- **THEN** the command SHALL continue to exit non-zero and SHALL display failed-source guidance
