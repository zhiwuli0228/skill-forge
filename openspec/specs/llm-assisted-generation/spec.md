# llm-assisted-generation Specification

## Purpose
Define the optional LLM-assisted refinement path for Skill generation while preserving the default deterministic local generation flow. This capability constrains LLM output to supported structured requirement fields and requires generated output to pass the same validation and quality reporting used by non-LLM generation.
## Requirements
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

### Requirement: LLM configuration errors are clear
The system SHALL fail clearly when LLM assistance is requested but provider configuration is incomplete.

#### Scenario: Missing LLM configuration
- **WHEN** a user runs `skill-forge create "<requirement>" --llm` without required LLM configuration
- **THEN** the command SHALL exit non-zero with a message naming the missing configuration

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

### Requirement: LLM assistance supports automatic and explicit modes
The system SHALL support LLM-assisted field generation through automatic selection by default, explicit force-enable mode, and explicit force-disable mode.

#### Scenario: Default create uses LLM when available
- **WHEN** a user runs `skill-forge create "<requirement>"`
- **AND** LLM configuration and availability checks pass
- **THEN** the system SHALL analyze the requirement and apply applicable blueprint defaults before sending structured requirement context to the configured LLM provider
- **AND** the system SHALL use valid returned structured fields when generating the Skill package

#### Scenario: Default create falls back without LLM
- **WHEN** a user runs `skill-forge create "<requirement>"`
- **AND** LLM configuration or availability checks do not pass
- **THEN** the system SHALL use deterministic generation without requiring the user to pass `--no-llm`

#### Scenario: Explicit LLM requests field generation
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **THEN** the system SHALL analyze the requirement and apply applicable blueprint defaults before sending structured requirement context to the configured LLM provider
- **AND** the system SHALL use valid returned structured fields when generating the Skill package

#### Scenario: Explicit no-LLM disables field generation
- **WHEN** a user runs `skill-forge create "<requirement>" --no-llm`
- **THEN** the system SHALL use the deterministic generation path without LLM configuration or network access

### Requirement: LLM assistance can use experience rules
The system SHALL allow LLM-assisted generation to receive applicable experience rules as prompt guidance before requesting structured requirement fields.

#### Scenario: LLM prompt includes applicable experience rules
- **WHEN** LLM-assisted generation runs for a requirement
- **AND** applicable experience rules exist for the current task type
- **THEN** the LLM request SHALL include compact experience rule guidance
- **AND** the request SHALL instruct the LLM to use those rules as guidance rather than as copied output

#### Scenario: No applicable experience keeps existing prompt
- **WHEN** LLM-assisted generation runs
- **AND** no applicable experience rules exist
- **THEN** generation SHALL continue with the existing LLM-assisted prompt context

#### Scenario: Experience preserves LLM fallback
- **WHEN** experience rules are included in an LLM-assisted generation request
- **AND** the LLM returns malformed fields or an unusable response
- **THEN** the system SHALL preserve the existing structured field validation and fallback behavior

### Requirement: LLM assistance can use retrieval context
The system SHALL allow LLM-assisted generation to receive compact reference patterns from similar high-quality local Skills before requesting structured requirement fields.

#### Scenario: LLM prompt includes retrieved patterns
- **WHEN** LLM-assisted generation runs for a requirement
- **AND** local retrieval returns relevant high-quality Skill references
- **THEN** the LLM request SHALL include compact workflow, constraint, and quality gate reference patterns derived from those references
- **AND** the request SHALL instruct the LLM to use the patterns as guidance rather than copied output

#### Scenario: Empty retrieval skips augmentation
- **WHEN** LLM-assisted generation runs
- **AND** the local corpus is empty or has too few quality Skill references
- **THEN** the system SHALL skip retrieval augmentation
- **AND** generation SHALL continue with the existing LLM-assisted prompt context

#### Scenario: Retrieval failure does not block generation
- **WHEN** retrieval augmentation fails while preparing an LLM-assisted generation request
- **THEN** the system SHALL continue LLM-assisted generation without retrieval context
- **AND** the LLM response SHALL still be processed through existing structured field validation and field-level fallback

### Requirement: Retrieval context preserves LLM fallback behavior
The system SHALL preserve the existing LLM structured output validation, unknown field handling, malformed field fallback, and unusable response fallback when retrieval context is present.

#### Scenario: Malformed LLM field falls back with RAG
- **WHEN** retrieval context is included in an LLM-assisted generation request
- **AND** the LLM returns a known field with an invalid type or no usable content
- **THEN** the system SHALL preserve the pre-LLM value for that field
- **AND** the system SHALL record that field as an LLM fallback field when provenance metadata is written

#### Scenario: Unknown LLM fields are ignored with RAG
- **WHEN** retrieval context is included in an LLM-assisted generation request
- **AND** the LLM returns fields that are not part of the supported requirement refinement schema
- **THEN** the system SHALL ignore those fields

### Requirement: LLM-assisted reference lookup can prefer promoted Skills
The system SHALL allow LLM-assisted local reference lookup to prefer
promoted Skills when high-quality local references are available.

#### Scenario: Promoted reference is selected
- **WHEN** local reference lookup finds both promoted and non-promoted
  Skills that satisfy the same relevance and quality gates
- **THEN** the system SHALL prefer the promoted Skill as a reference
  candidate

#### Scenario: Promotion does not bypass quality gates
- **WHEN** a promoted Skill fails the existing relevance or content
  quality thresholds
- **THEN** the system SHALL NOT use promotion alone to force that Skill
  into the LLM-assisted reference context

#### Scenario: No promoted references remains valid
- **WHEN** local reference lookup finds no promoted Skills
- **THEN** the system SHALL preserve the existing reference-selection
  behavior

