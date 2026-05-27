## ADDED Requirements

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
