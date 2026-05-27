# research-corpus-update Specification

## Purpose
Define how Skill Forge refreshes configured research sources into the local corpus, records source/document metadata, handles partial failures, and reports source update quality so users can trust and troubleshoot the local reference layer.
## Requirements
### Requirement: Update command refreshes configured research corpus
The system SHALL provide an `update` command that refreshes enabled Skill research sources into the local corpus.

#### Scenario: Update reads configured sources
- **WHEN** a user runs `skill-forge update`
- **THEN** the system SHALL load enabled sources from `~/.skill-forge/sources.yaml` if present, otherwise from `configs/sources.yaml`

#### Scenario: Update reports source outcomes
- **WHEN** update completes
- **THEN** the command SHALL display counts for successful, skipped, and failed source updates

### Requirement: Source configuration is structured
The system SHALL define structured source records for research updates.

#### Scenario: Default source config exists
- **WHEN** the project is installed
- **THEN** `configs/sources.yaml` SHALL define named sources with type, URL, authority level, and enabled flag

#### Scenario: Disabled sources are skipped
- **WHEN** a configured source has `enabled: false`
- **THEN** update SHALL skip that source without fetching it

### Requirement: Fetched content is cached in layers
The updater SHALL save fetched source content into raw and normalized corpus cache layers.

#### Scenario: Successful source writes raw and normalized files
- **WHEN** an enabled source is fetched successfully
- **THEN** the updater SHALL save raw content under the raw corpus directory and normalized content under the normalized corpus directory

#### Scenario: Normalized content is text oriented
- **WHEN** fetched content is HTML or Markdown-like text
- **THEN** the normalized cache SHALL contain readable text or Markdown suitable for later indexing

### Requirement: Corpus metadata is persisted in SQLite
The updater SHALL persist source, document, and skill example metadata in SQLite.

#### Scenario: Successful update writes metadata
- **WHEN** an enabled source is fetched successfully
- **THEN** SQLite SHALL contain source metadata, document URL/path/hash metadata, and at least one extracted skill example or document summary record when extractable

#### Scenario: Repeated unchanged update is skipped
- **WHEN** a source fetch returns the same content hash as an existing document
- **THEN** the updater SHALL skip rewriting normalized content and report the source as skipped

### Requirement: Update handles partial failures
The updater SHALL continue processing enabled sources when individual sources fail.

#### Scenario: One source fails and another succeeds
- **WHEN** at least one enabled source fails and at least one enabled source succeeds or is skipped
- **THEN** update SHALL complete successfully and report the failed source

#### Scenario: All enabled sources fail
- **WHEN** all enabled sources fail to fetch or process
- **THEN** update SHALL return a non-zero exit code

### Requirement: Research update is covered by automated tests
The system SHALL include automated tests for research update behavior.

#### Scenario: Tests cover update workflow
- **WHEN** the test suite runs
- **THEN** it SHALL verify source loading, disabled source skipping, raw/normalized cache writes, SQLite metadata writes, hash skip behavior, partial failure success, all-failure non-zero behavior, and CLI update integration using mocked fetchers

### Requirement: Update summary reports full source status
The system SHALL summarize research update outcomes across updated, skipped, failed, and disabled sources.

#### Scenario: Summary includes disabled sources
- **WHEN** a user runs `skill-forge update` and one or more configured sources are disabled
- **THEN** the command SHALL display the disabled source count in the update summary

#### Scenario: Partial update is identified
- **WHEN** a user runs `skill-forge update` and at least one enabled source succeeds while another enabled source fails
- **THEN** the command SHALL identify the update as partial while still exiting successfully

### Requirement: Failed source outcomes include retry guidance
The system SHALL provide deterministic retry guidance for failed research source updates.

#### Scenario: Failed source displays guidance
- **WHEN** a source update fails
- **THEN** the update output SHALL include the failure message and guidance to retry with `skill-forge update` after resolving the source issue

#### Scenario: All sources fail remains non-zero
- **WHEN** all enabled sources fail during update
- **THEN** the command SHALL continue to exit non-zero and SHALL display failed-source guidance
