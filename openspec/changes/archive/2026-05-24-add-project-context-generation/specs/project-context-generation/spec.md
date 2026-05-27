## ADDED Requirements

### Requirement: Project context reader scans bounded project files
The system SHALL read project context from a bounded set of rule and documentation files under a user-provided project path.

#### Scenario: Reader detects supported project files
- **WHEN** a project contains files or directories such as `AGENTS.md`, `CLAUDE.md`, `README.md`, `.opencode/`, `.claude/`, `.agents/`, `openspec/`, `config.yaml`, or `project.md`
- **THEN** the reader SHALL include eligible text content from those paths in the project context input

#### Scenario: Reader skips unsafe or noisy files
- **WHEN** a candidate file is binary, larger than the configured per-file size limit, or located under dependency/build output directories
- **THEN** the reader SHALL skip that file and record it as skipped

#### Scenario: Reader respects total context limits
- **WHEN** eligible project files exceed the configured total character limit
- **THEN** the reader SHALL stop adding content after the limit and preserve a deterministic file order

### Requirement: Project context summary is deterministic
The system SHALL produce a deterministic project context summary without requiring an LLM.

#### Scenario: Summary detects agent tooling
- **WHEN** project files indicate OpenSpec, opencode, Claude, Codex, or AGENTS-style rules
- **THEN** the summary SHALL include those detected agent tools

#### Scenario: Summary detects workflow rules
- **WHEN** project files contain rules about OpenSpec changes, tests, unrelated modifications, or implementation workflow
- **THEN** the summary SHALL include concise detected rules

### Requirement: Project context becomes Skill constraints
The system SHALL convert project context into Skill constraints suitable for generated `SKILL.md` content.

#### Scenario: Context constraints are injected
- **WHEN** a Skill is generated with project context
- **THEN** the generated Skill SHALL include constraints derived from the project context summary

#### Scenario: Context constraints are deduplicated
- **WHEN** project-derived constraints overlap existing requirement constraints
- **THEN** the system SHALL avoid duplicate constraint entries

### Requirement: Interactive project context is persisted in drafts
The system SHALL persist project context data when project-aware generation is used with interactive drafts.

#### Scenario: Interactive draft stores project context
- **WHEN** a user runs `skill-forge create "<requirement>" --project <path> --interactive`
- **THEN** the draft JSON SHALL include the project path and project context summary

#### Scenario: Resume uses stored project context
- **WHEN** a user resumes a draft that contains project context data
- **THEN** the system SHALL continue using the stored project context data without requiring a rescan

### Requirement: Project context behavior is covered by automated tests
The system SHALL include automated tests for project context generation behavior.

#### Scenario: Tests cover project context workflow
- **WHEN** the test suite runs
- **THEN** it SHALL verify project file scanning, skip rules, deterministic summaries, constraint injection, interactive draft persistence, resume behavior, and CLI create integration
