## MODIFIED Requirements

### Requirement: LLM assistance is opt-in
The system SHALL provide optional LLM-assisted field generation for Skill generation only when explicitly requested by the user.

#### Scenario: Default create does not use LLM
- **WHEN** a user runs `skill-forge create "<requirement>"` without `--llm`
- **THEN** the system SHALL use the existing deterministic generation path without requiring LLM configuration or network access

#### Scenario: Create with LLM requests field generation
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **THEN** the system SHALL analyze the requirement and apply applicable blueprint defaults before sending structured requirement context to the configured LLM provider
- **AND** the system SHALL use valid returned structured fields when generating the Skill package

### Requirement: LLM output is constrained to structured requirement fields
The system SHALL accept only known structured requirement fields from LLM responses and SHALL preserve required baseline fields needed for rendering.

#### Scenario: LLM generates core requirement content
- **WHEN** the configured LLM returns valid structured list fields for workflow, constraints, or quality gates
- **THEN** the system SHALL merge those fields into the enriched Skill requirement before generation

#### Scenario: LLM refines descriptive requirement content
- **WHEN** the configured LLM returns valid structured descriptive fields such as description, usage boundaries, required inputs, expected outputs, domain, or task type
- **THEN** the system SHALL merge those fields into the enriched Skill requirement before generation

#### Scenario: Unknown response fields are ignored
- **WHEN** the configured LLM returns fields that are not part of the supported requirement refinement schema
- **THEN** the system SHALL ignore those fields

#### Scenario: Malformed known field falls back
- **WHEN** the configured LLM returns a known field with an invalid type or no usable content
- **THEN** the system SHALL preserve the pre-LLM value for that field
- **AND** the system SHALL record that field as an LLM fallback field when provenance metadata is written

#### Scenario: Unusable LLM response falls back
- **WHEN** the configured LLM returns empty content, malformed JSON, or a top-level value that is not a JSON object
- **THEN** `skill-forge create --llm` SHALL continue generation from the pre-LLM enriched requirement
- **AND** the system SHALL record LLM fallback fields when provenance metadata is written

### Requirement: LLM-assisted output is validated
The system SHALL validate and quality-report generated packages after LLM-assisted field generation.

#### Scenario: LLM-assisted create reports quality
- **WHEN** `skill-forge create "<requirement>" --llm` generates a Skill package
- **THEN** the system SHALL run post-generation validation
- **AND** the system SHALL display the same validation quality report format used by deterministic generation
- **AND** the report SHALL include deterministic content quality metrics when they are available

### Requirement: LLM assistance is covered by automated tests
The system SHALL include automated tests for LLM field generation, field fallback, configuration failures, and default deterministic behavior.

#### Scenario: Tests cover default path
- **WHEN** the test suite runs
- **THEN** it SHALL verify that create without `--llm` does not require LLM configuration

#### Scenario: Tests cover LLM field generation
- **WHEN** the test suite runs
- **THEN** it SHALL verify successful generation of workflow, constraints, and quality gates from valid LLM responses

#### Scenario: Tests cover LLM fallback
- **WHEN** the test suite runs
- **THEN** it SHALL verify malformed known fields, empty responses, malformed JSON, unknown fields, and missing configuration handling
