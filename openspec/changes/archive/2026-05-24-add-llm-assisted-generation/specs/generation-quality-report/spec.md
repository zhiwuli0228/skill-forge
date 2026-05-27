## ADDED Requirements

### Requirement: LLM-assisted generation uses quality reporting
The system SHALL use the same post-generation quality report for LLM-assisted generation as for deterministic generation.

#### Scenario: LLM-assisted output displays quality score
- **WHEN** `skill-forge create "<requirement>" --llm` completes generation
- **THEN** the system SHALL display validation status, quality score, validation issues, and next actions
