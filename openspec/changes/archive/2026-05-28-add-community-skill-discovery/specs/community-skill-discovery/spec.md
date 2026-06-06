## ADDED Requirements

### Requirement: GitHub sources can declare Skill discovery
The system SHALL allow configured GitHub research sources to opt into repository-scoped Skill discovery through structured source metadata.

#### Scenario: GitHub source declares discovery patterns
- **WHEN** a GitHub source includes discovery metadata with `skill_file_patterns`
- **THEN** the updater SHALL treat the source as a repository discovery source rather than a single-page fetch source

#### Scenario: GitHub source without discovery metadata keeps existing behavior
- **WHEN** a GitHub source does not include discovery metadata
- **THEN** the updater SHALL preserve the existing single-source fetch behavior

### Requirement: Discovery finds candidate SKILL.md files
The system SHALL discover candidate Skill files from configured GitHub repositories by matching repository file paths against configured discovery patterns.

#### Scenario: Matching Skill files are discovered
- **WHEN** repository tree data contains paths matching configured `skill_file_patterns`
- **THEN** the discovery process SHALL return those matching `SKILL.md` paths as candidate Skills

#### Scenario: Non-matching files are ignored
- **WHEN** repository tree data contains files that do not match configured Skill file patterns
- **THEN** those files SHALL NOT be fetched as discovered Skills

#### Scenario: Discovery supports platform-specific paths
- **WHEN** a source config includes patterns for `.codex/skills/*/SKILL.md`, `.claude/skills/*/SKILL.md`, or `.opencode/skills/*/SKILL.md`
- **THEN** matching platform-specific Skill files SHALL be discoverable

### Requirement: Discovered Skills are fetched and parsed individually
The system SHALL fetch each discovered Skill file and parse it into individual Skill example metadata.

#### Scenario: Discovered Skill creates metadata
- **WHEN** a discovered `SKILL.md` contains frontmatter with `name` and `description`
- **THEN** the system SHALL create a Skill example using the frontmatter name and description

#### Scenario: Missing frontmatter uses fallbacks
- **WHEN** a discovered `SKILL.md` is readable but lacks complete frontmatter
- **THEN** the system SHALL derive fallback name or summary metadata from the file path and normalized content

#### Scenario: Platform metadata is preserved
- **WHEN** a source config includes platform metadata
- **THEN** discovered Skill examples SHALL preserve that platform value

#### Scenario: Tags metadata is preserved
- **WHEN** a source config includes tags metadata
- **THEN** discovered Skill examples SHALL include those tags in stored metadata

### Requirement: Discovered Skills are cached as separate corpus documents
The system SHALL store each discovered Skill as a separate raw and normalized corpus document with stable per-file metadata.

#### Scenario: Each discovered Skill writes cache files
- **WHEN** a discovered Skill is fetched successfully
- **THEN** the updater SHALL write raw and normalized cache files for that Skill

#### Scenario: Each discovered Skill has a document row
- **WHEN** a discovered Skill is stored successfully
- **THEN** SQLite SHALL contain a document row whose URL identifies that specific repository file

#### Scenario: Each discovered Skill has a skill example row
- **WHEN** a discovered Skill is stored successfully
- **THEN** SQLite SHALL contain a `skill_examples` row for that specific Skill

#### Scenario: Repeated unchanged discovered Skill is skipped
- **WHEN** a later update fetches a discovered Skill with the same content hash as an existing document
- **THEN** the updater SHALL skip rewriting that Skill's normalized content

### Requirement: Discovery handles partial failures
The system SHALL continue processing other discovered Skills when individual Skill files fail to fetch or parse.

#### Scenario: One discovered Skill fails and another succeeds
- **WHEN** one discovered Skill file fails and another discovered Skill file is stored successfully
- **THEN** update SHALL complete successfully and report both outcomes

#### Scenario: No discovered Skills can be stored
- **WHEN** discovery finds candidates but none can be fetched or stored successfully
- **THEN** update SHALL report a failed outcome for that source

### Requirement: Community discovery is covered by automated tests
The system SHALL include automated tests for GitHub community Skill discovery without depending on live network access.

#### Scenario: Tests cover repository discovery
- **WHEN** the test suite runs
- **THEN** it SHALL verify discovery pattern matching, per-Skill fetching, frontmatter extraction, fallback metadata, cache writes, hash skip behavior, and partial failure handling using mocked GitHub responses
