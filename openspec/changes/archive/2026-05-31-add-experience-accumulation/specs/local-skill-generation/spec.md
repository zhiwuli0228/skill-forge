## ADDED Requirements

### Requirement: Generation can apply local experience rules
The system SHALL allow non-interactive generation to apply applicable local experience rules as optional guidance.

#### Scenario: Deterministic generation applies matching rules
- **WHEN** deterministic generation runs for a requirement with task type matching stored experience rules
- **THEN** the system SHALL apply relevant rules to improve generated workflow, constraints, or quality gates when the rule can be applied without conflicting with user-provided requirement fields

#### Scenario: LLM-assisted generation applies matching rules
- **WHEN** LLM-assisted generation runs for a requirement with task type matching stored experience rules
- **THEN** the system SHALL include applicable rules in the LLM context before field generation

#### Scenario: No experience preserves baseline generation
- **WHEN** no applicable experience rules exist
- **THEN** generation SHALL preserve the existing deterministic or LLM-assisted behavior

### Requirement: Generated metadata records experience usage
The system SHALL record applied experience rule IDs in provenance metadata for generated non-interactive Skill packages.

#### Scenario: Metadata records applied rules
- **WHEN** generation applies one or more experience rules
- **THEN** `skill-forge.json` SHALL record the applied experience rule IDs

#### Scenario: Metadata records no applied rules
- **WHEN** generation completes without applying experience rules
- **THEN** `skill-forge.json` SHALL record an empty applied experience rule list
