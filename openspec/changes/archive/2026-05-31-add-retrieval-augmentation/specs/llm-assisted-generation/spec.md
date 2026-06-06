## ADDED Requirements

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
