## ADDED Requirements

### Requirement: Search supports optional reranking
The system SHALL allow users to opt into a second-stage rerank pass for search results.

#### Scenario: Default search remains TF-IDF
- **WHEN** a user runs `skill-forge search "<query>"` without rerank enabled
- **THEN** the system SHALL use the existing TF-IDF ranking behavior

#### Scenario: User enables rerank
- **WHEN** a user runs `skill-forge search "<query>" --rerank`
- **THEN** the system SHALL rerank TF-IDF candidate results before displaying the final results

#### Scenario: Search output identifies rerank mode
- **WHEN** rerank is enabled for a search command
- **THEN** the output SHALL identify the retrieval mode as reranked

### Requirement: Rerank remains local and optional
The system SHALL provide an offline rerank implementation and SHALL NOT require network access or model downloads.

#### Scenario: Built-in rerank runs offline
- **WHEN** a user enables rerank with the built-in reranker
- **THEN** the rerank pass SHALL run without network access and without downloading external models

#### Scenario: Create does not use rerank
- **WHEN** a user runs `skill-forge create`
- **THEN** the system SHALL NOT invoke retrieval rerank

### Requirement: Rerank failure falls back clearly
The system SHALL preserve search availability when optional rerank fails.

#### Scenario: Reranker failure falls back to TF-IDF
- **WHEN** rerank is enabled and the reranker fails
- **THEN** the command SHALL display TF-IDF-ranked results and a clear fallback warning

#### Scenario: Rerank disabled by configuration
- **WHEN** rerank is requested but retrieval configuration disables rerank
- **THEN** the command SHALL display TF-IDF-ranked results and a clear disabled-rerank warning
