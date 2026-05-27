## ADDED Requirements

### Requirement: Retrieval configuration controls rerank
The system SHALL include configuration fields that control optional search reranking.

#### Scenario: Default config disables rerank
- **WHEN** Skill Forge creates or loads default configuration
- **THEN** rerank SHALL be disabled by default while TF-IDF search remains enabled

#### Scenario: Config can enable rerank by default
- **WHEN** retrieval configuration enables rerank by default
- **THEN** `skill-forge search` SHALL use rerank without requiring the `--rerank` flag

#### Scenario: Config can disable rerank availability
- **WHEN** retrieval configuration disables rerank availability
- **THEN** `skill-forge search --rerank` SHALL fall back to TF-IDF with a clear warning
