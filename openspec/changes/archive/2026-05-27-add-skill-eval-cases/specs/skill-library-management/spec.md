## ADDED Requirements

### Requirement: Library inspection shows eval summary
The system SHALL display the latest eval summary for a generated Skill package when an eval report exists.

#### Scenario: Show generated Skill with eval summary
- **WHEN** a user runs `skill-forge show <skill-name>` for a package containing `eval-report.json`
- **THEN** the command SHALL display total, passed, and failed eval counts

#### Scenario: Show generated Skill without eval summary
- **WHEN** a user runs `skill-forge show <skill-name>` for a package without `eval-report.json`
- **THEN** the command SHALL continue to display generated Skill metadata without failing
