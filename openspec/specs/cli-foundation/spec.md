# cli-foundation Specification

## Purpose
Define the foundational Skill Forge CLI application, local workspace initialization, default configuration behavior, and baseline SQLite schema used by later capabilities.
## Requirements
### Requirement: CLI application exposes foundational commands
The system SHALL expose a Typer-based `skill-forge` CLI application through the existing package script entry point.

#### Scenario: CLI help is available
- **WHEN** a user runs `skill-forge --help`
- **THEN** the command SHALL complete successfully and display the available foundational commands including `init`

#### Scenario: Package main delegates to CLI
- **WHEN** the installed `skill-forge` script invokes `skill_forge:main`
- **THEN** execution SHALL be handled by the Typer CLI application rather than printing the placeholder message

### Requirement: Init command creates local workspace
The system SHALL provide an `init` command that creates the standard Skill Forge local workspace under `~/.skill-forge` by default.

#### Scenario: First initialization creates standard directories
- **WHEN** a user runs `skill-forge init` for the first time
- **THEN** the system SHALL create `~/.skill-forge/config.yaml`, `~/.skill-forge/db/skill_forge.sqlite`, `~/.skill-forge/corpus/`, `~/.skill-forge/drafts/`, `~/.skill-forge/output/`, `~/.skill-forge/index/`, and `~/.skill-forge/logs/`

#### Scenario: Repeated initialization is idempotent
- **WHEN** a user runs `skill-forge init` after the workspace already exists
- **THEN** the command SHALL complete successfully without deleting existing workspace files

### Requirement: Default configuration is generated and loadable
The system SHALL generate and load a default configuration for update, create, retrieval, and platform path settings.

#### Scenario: Missing config uses documented defaults
- **WHEN** the system loads configuration and no user config exists
- **THEN** it SHALL use defaults for manual updates, seven day stale threshold, opencode as the default target, Chinese as the default language, top-k retrieval of five, and user skill paths for opencode, Claude, and Codex

#### Scenario: Init preserves existing user config
- **WHEN** `skill-forge init` runs and `~/.skill-forge/config.yaml` already exists
- **THEN** the system SHALL leave the existing config file in place

### Requirement: SQLite baseline schema is initialized
The system SHALL initialize a SQLite database with the baseline metadata tables required by later changes.

#### Scenario: Database file and baseline tables are created
- **WHEN** a user runs `skill-forge init`
- **THEN** the system SHALL create `~/.skill-forge/db/skill_forge.sqlite` with baseline tables for `sources`, `documents`, `skill_examples`, `skill_patterns`, and `drafts`

#### Scenario: Database initialization can run repeatedly
- **WHEN** database initialization runs against an existing database file
- **THEN** the system SHALL keep existing tables and complete without schema creation errors

### Requirement: Foundation behavior is covered by tests
The system SHALL include focused automated tests for the CLI foundation.

#### Scenario: Tests validate initialization behavior
- **WHEN** the test suite runs
- **THEN** it SHALL verify CLI help, default configuration behavior, workspace directory creation, config preservation, and SQLite baseline schema creation using isolated test paths

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
