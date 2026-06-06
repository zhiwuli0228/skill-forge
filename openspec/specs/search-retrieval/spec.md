# search-retrieval Specification

## Purpose
Define how Skill Forge searches the local research corpus using TF-IDF retrieval plus deterministic quality signals, including optional score explanation and optional local reranking for users who need to understand or refine ranking behavior.
## Requirements
### Requirement: Search command queries local research corpus
The system SHALL provide a `search` command that queries locally cached research corpus content without performing network refresh.

#### Scenario: Search returns matching corpus results
- **WHEN** a user runs `skill-forge search "skill creator"` and the local corpus contains matching documents
- **THEN** the system SHALL return ranked results from the local corpus

#### Scenario: Search does not update remote sources
- **WHEN** a user runs `skill-forge search "skill creator"`
- **THEN** the system SHALL NOT fetch remote source content or run the research updater

### Requirement: Search supports top-k result limits
The search command SHALL allow users to control the maximum number of displayed results.

#### Scenario: Search limits result count
- **WHEN** a user runs `skill-forge search "bug investigation" --top-k 3`
- **THEN** the system SHALL display no more than 3 results

#### Scenario: Search uses configured default top-k
- **WHEN** a user runs `skill-forge search "bug investigation"` without `--top-k`
- **THEN** the system SHALL use the configured retrieval default top-k value

### Requirement: TF-IDF index is built from local corpus
The system SHALL build a TF-IDF index from normalized corpus content and SQLite metadata.

#### Scenario: Missing index is built automatically
- **WHEN** search is run and no usable local TF-IDF index exists
- **THEN** the system SHALL build an index from available corpus documents before searching

#### Scenario: Stale index is rebuilt automatically
- **WHEN** search is run and corpus metadata has changed since the index was built
- **THEN** the system SHALL rebuild the TF-IDF index before searching

### Requirement: Search results include useful metadata
Search results SHALL include enough metadata for users to evaluate reference usefulness.

#### Scenario: Result output includes reference fields
- **WHEN** search returns a result
- **THEN** the result SHALL include name or title, source, platform when known, summary, and score

### Requirement: Search ranking combines relevance and quality signals
The system SHALL rank search results using text relevance plus deterministic quality signals.

#### Scenario: Text relevance affects ranking
- **WHEN** multiple corpus entries match a query with different TF-IDF relevance
- **THEN** entries with stronger text relevance SHALL rank higher when other signals are equal

#### Scenario: Authority and completeness affect ranking
- **WHEN** corpus entries have similar text relevance
- **THEN** official or more complete entries SHALL receive a ranking boost over lower authority or sparse entries

#### Scenario: Platform match affects ranking
- **WHEN** a user searches with a target platform option
- **THEN** entries matching that platform SHALL receive a ranking boost

### Requirement: Empty corpus search is user friendly
The system SHALL handle missing or empty local corpus data with a clear message.

#### Scenario: Search before update
- **WHEN** a user runs search and no corpus documents are available
- **THEN** the system SHALL display a clear message that the local corpus is empty and suggest running `skill-forge update`

### Requirement: Search retrieval is covered by automated tests
The system SHALL include automated tests for search retrieval behavior.

#### Scenario: Tests cover search workflow
- **WHEN** the test suite runs
- **THEN** it SHALL verify index building, stale index rebuild, top-k handling, metadata output, ranking boosts, empty corpus behavior, and CLI search integration

### Requirement: Search can explain ranking scores
The system SHALL provide an optional search explanation mode that displays deterministic score components for each returned result.

#### Scenario: Explain search scores
- **WHEN** a user runs `skill-forge search "<query>" --explain`
- **THEN** each displayed result SHALL include relevance, authority, completeness, freshness, platform boost, and final score values

#### Scenario: Default search remains compact
- **WHEN** a user runs `skill-forge search "<query>"` without `--explain`
- **THEN** the command SHALL display the normal compact search result table without score component explanation columns

### Requirement: Search explanation reflects existing ranking components
The system SHALL use the same ranking component values already used to calculate returned search scores.

#### Scenario: Platform boost is visible
- **WHEN** a user runs search with both `--platform <platform>` and `--explain`
- **THEN** results matching the requested platform SHALL display a positive platform boost

#### Scenario: Freshness boost is visible
- **WHEN** a returned result has a freshness boost from recent corpus metadata and `--explain` is enabled
- **THEN** the output SHALL display that freshness boost value

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

### Requirement: Search results expose adoptable corpus references
The system SHALL include stable local corpus references in search results so users can adopt cached Skill documents.

#### Scenario: Search result includes document ID
- **WHEN** search returns a corpus result
- **THEN** the result SHALL include the local corpus document ID

#### Scenario: Search result includes example ID when available
- **WHEN** search returns a corpus result associated with a skill example row
- **THEN** the result SHALL include the local skill example ID

#### Scenario: Search reference is local
- **WHEN** search displays corpus reference IDs
- **THEN** those IDs SHALL refer to locally cached corpus records and SHALL NOT require network access to resolve

### Requirement: Search output supports adoption workflow
The search command SHALL display enough reference metadata for a user to run the adoption command for a returned result.

#### Scenario: Search output shows adoptable ID
- **WHEN** a user runs `skill-forge search "<query>"`
- **THEN** the command output SHALL show the document ID or another documented local reference that can be passed to `skill-forge adopt`

#### Scenario: Empty search remains unchanged
- **WHEN** search returns no results
- **THEN** the command SHALL preserve the existing empty-result behavior and SHALL NOT display adoption guidance for missing results
