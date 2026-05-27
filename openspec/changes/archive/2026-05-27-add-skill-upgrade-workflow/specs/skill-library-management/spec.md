## ADDED Requirements

### Requirement: Upgrade candidates are library packages
The system SHALL manage upgrade candidate packages as generated Skill library packages.

#### Scenario: List upgrade candidate
- **WHEN** an upgrade candidate package exists in the generated Skill output directory
- **THEN** `skill-forge list` SHALL display it as a generated Skill package

#### Scenario: Show upgrade candidate
- **WHEN** a user runs `skill-forge show <candidate-name>` for an upgrade candidate package
- **THEN** the command SHALL display the candidate package metadata and provenance like any other generated Skill package

#### Scenario: Diff source and upgrade candidate
- **WHEN** a user runs `skill-forge diff <source-skill> <candidate-name>`
- **THEN** the command SHALL compare the source and candidate packages using the existing generated Skill diff behavior
