## ADDED Requirements

### Requirement: Retrieval supports generation reference lookup
The system SHALL expose local TF-IDF retrieval results for LLM-assisted generation as a non-blocking source of similar Skill references without changing default search behavior.

#### Scenario: Generation lookup uses local retrieval
- **WHEN** LLM-assisted generation requests similar Skill references
- **THEN** the system SHALL query the existing local TF-IDF retrieval index
- **AND** it SHALL NOT fetch remote source content
- **AND** it SHALL NOT require vector search or external model dependencies

#### Scenario: Generation lookup applies quality gates
- **WHEN** local retrieval returns candidate references for generation
- **THEN** the system SHALL filter or skip candidates that do not meet configured relevance and content-quality thresholds

#### Scenario: Generation lookup does not use rerank
- **WHEN** LLM-assisted generation requests similar Skill references
- **THEN** the system SHALL NOT invoke optional search rerank behavior

#### Scenario: Search command behavior remains unchanged
- **WHEN** a user runs `skill-forge search "<query>"`
- **THEN** the command SHALL preserve its existing TF-IDF search behavior and output contract
