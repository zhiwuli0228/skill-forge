## ADDED Requirements

### Requirement: Semantic retrieval is optional
The system SHALL provide semantic Skill retrieval only as an optional
mode and SHALL preserve the existing non-semantic default behavior.

#### Scenario: Default search remains unchanged
- **WHEN** a user runs `skill-forge search "<query>"` without a semantic
  option
- **THEN** the system SHALL preserve the existing default retrieval
  behavior

#### Scenario: Semantic mode is explicit
- **WHEN** a user requests semantic retrieval
- **THEN** the system SHALL run the semantic path only for that request
  or equivalent explicit configuration

### Requirement: Semantic retrieval remains local-first
The system SHALL support semantic retrieval without requiring a hosted
vector database or mandatory network dependency.

#### Scenario: Local semantic index is used
- **WHEN** semantic retrieval is available
- **THEN** the system SHALL query a local semantic index or equivalent
  local provider output

#### Scenario: Semantic index missing falls back clearly
- **WHEN** semantic retrieval is requested but the semantic index is
  unavailable
- **THEN** the system SHALL fall back to the existing retrieval mode or
  fail with a clear local-only guidance message

### Requirement: Semantic retrieval supports collection-aware similarity
The system SHALL allow semantic retrieval to work with curated or
promoted collections as a preferred local subset.

#### Scenario: Search within promoted collection
- **WHEN** a user requests semantic retrieval against promoted Skills
- **THEN** the system SHALL restrict or prioritize semantic candidates
  from the promoted collection set

#### Scenario: Similarity results are explainable
- **WHEN** semantic retrieval returns a local Skill reference
- **THEN** the system SHALL provide enough metadata to explain which
  local Skill was matched and what mode was used
