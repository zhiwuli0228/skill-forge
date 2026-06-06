## ADDED Requirements

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
