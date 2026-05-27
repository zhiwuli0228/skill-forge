# llm-assisted-generation Specification

## Purpose
Define the optional LLM-assisted refinement path for Skill generation while preserving the default deterministic local generation flow. This capability constrains LLM output to supported structured requirement fields and requires generated output to pass the same validation and quality reporting used by non-LLM generation.
## Requirements
### Requirement: LLM assistance is opt-in
The system SHALL provide optional LLM-assisted refinement for Skill generation only when explicitly requested by the user.

#### Scenario: Default create does not use LLM
- **WHEN** a user runs `skill-forge create "<requirement>"` without `--llm`
- **THEN** the system SHALL use the existing deterministic generation path without requiring LLM configuration or network access

#### Scenario: Create with LLM requests refinement
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **THEN** the system SHALL send structured requirement context to the configured LLM provider before rendering the Skill package
- **AND** the system SHALL use the returned structured refinement when generating the Skill package

### Requirement: LLM output is constrained to structured requirement fields
The system SHALL accept only known structured requirement fields from LLM responses and SHALL preserve required baseline fields needed for rendering.

#### Scenario: LLM refines requirement content
- **WHEN** the configured LLM returns structured fields such as description, workflow, constraints, expected outputs, or quality gates
- **THEN** the system SHALL merge those fields into the analyzed Skill requirement before generation

#### Scenario: Unknown response fields are ignored
- **WHEN** the configured LLM returns fields that are not part of the supported requirement refinement schema
- **THEN** the system SHALL ignore those fields

#### Scenario: Malformed LLM response fails clearly
- **WHEN** the configured LLM returns malformed JSON or an invalid structured response
- **THEN** `skill-forge create --llm` SHALL exit non-zero with a clear LLM response error

### Requirement: LLM configuration errors are clear
The system SHALL fail clearly when LLM assistance is requested but provider configuration is incomplete.

#### Scenario: Missing LLM configuration
- **WHEN** a user runs `skill-forge create "<requirement>" --llm` without required LLM configuration
- **THEN** the command SHALL exit non-zero with a message naming the missing configuration

### Requirement: LLM-assisted output is validated
The system SHALL validate and quality-report generated packages after LLM-assisted refinement.

#### Scenario: LLM-assisted create reports quality
- **WHEN** `skill-forge create "<requirement>" --llm` generates a Skill package
- **THEN** the system SHALL run post-generation validation
- **AND** the system SHALL display the same quality report format used by deterministic generation

### Requirement: LLM assistance is covered by automated tests
The system SHALL include automated tests for LLM refinement, configuration failures, and default deterministic behavior.

#### Scenario: Tests cover default path
- **WHEN** the test suite runs
- **THEN** it SHALL verify that create without `--llm` does not require LLM configuration

#### Scenario: Tests cover LLM path
- **WHEN** the test suite runs
- **THEN** it SHALL verify successful LLM refinement, malformed response handling, and missing configuration handling
