## ADDED Requirements

### Requirement: Generated metadata records retrieval augmentation
The system SHALL record retrieval augmentation status in provenance metadata for generated non-interactive Skill packages when LLM-assisted generation is selected.

#### Scenario: Metadata records used retrieval context
- **WHEN** `skill-forge create "<requirement>" --llm` completes successfully
- **AND** retrieval augmentation supplied reference patterns to the LLM request
- **THEN** `skill-forge.json` SHALL record that retrieval augmentation was used
- **AND** it SHALL record the referenced Skill names or identifiers

#### Scenario: Metadata records skipped retrieval context
- **WHEN** LLM-assisted generation completes without retrieval context because the local corpus was empty, insufficient, below quality thresholds, or retrieval failed
- **THEN** `skill-forge.json` SHALL record that retrieval augmentation was not used
- **AND** it SHALL record a skipped or fallback reason

#### Scenario: Deterministic generation omits RAG work
- **WHEN** a user runs `skill-forge create "<requirement>" --no-llm`
- **THEN** the system SHALL NOT perform retrieval augmentation
- **AND** generated metadata SHALL NOT claim that retrieval augmentation was used
