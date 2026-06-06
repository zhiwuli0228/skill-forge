## ADDED Requirements

### Requirement: Eval reports can feed experience derivation
The system SHALL make persisted eval reports available as local evidence for experience rule derivation.

#### Scenario: Failed assertions are available as evidence
- **WHEN** an eval report contains failed assertions for a generated Skill package
- **THEN** experience derivation SHALL be able to read the failed assertion names, messages, case IDs, and package name as evidence

#### Scenario: Passing eval reports do not create failure rules
- **WHEN** an eval report contains no failed assertions
- **THEN** experience derivation SHALL NOT derive failure-pattern rules from that report

#### Scenario: Missing eval reports are skipped
- **WHEN** a generated Skill package has no persisted eval report
- **THEN** experience derivation SHALL skip eval evidence for that package without failing
