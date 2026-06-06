## ADDED Requirements

### Requirement: Content quality metrics can feed experience derivation
The system SHALL make deterministic content quality metrics available as local evidence for experience rule derivation.

#### Scenario: Low workflow score is evidence
- **WHEN** generated package provenance includes a low workflow specificity score
- **THEN** experience derivation SHALL be able to use that score as evidence for a workflow-improvement rule

#### Scenario: Low constraint score is evidence
- **WHEN** generated package provenance includes a low constraint verifiability score
- **THEN** experience derivation SHALL be able to use that score as evidence for a constraint-improvement rule

#### Scenario: Low quality gate score is evidence
- **WHEN** generated package provenance includes a low quality gate clarity score
- **THEN** experience derivation SHALL be able to use that score as evidence for a quality-gate-improvement rule

#### Scenario: Missing content quality is skipped
- **WHEN** generated package provenance has no content quality metrics
- **THEN** experience derivation SHALL skip quality evidence for that package without failing
