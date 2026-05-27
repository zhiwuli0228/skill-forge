# skill-library-management Specification

## Purpose
Define how Skill Forge discovers, lists, inspects, and compares generated Skill packages from the configured output directory. This capability gives users a local library view over generated Skills without changing generation quality logic or introducing a remote marketplace.
## Requirements
### Requirement: List generated Skills
The system SHALL provide a command that lists generated Skill packages from the configured output directory.

#### Scenario: List generated packages
- **WHEN** a user runs `skill-forge list`
- **THEN** the system SHALL display generated Skill package entries found under the configured output directory

#### Scenario: Empty library list
- **WHEN** no generated Skill packages exist in the configured output directory
- **THEN** the system SHALL display a clear empty-library message and exit successfully

### Requirement: Show generated Skill metadata
The system SHALL provide a command that displays metadata for a selected generated Skill package.

#### Scenario: Show existing generated Skill
- **WHEN** a user runs `skill-forge show <skill-name>` for an existing generated package
- **THEN** the system SHALL display the package path, `SKILL.md` path, frontmatter name, description, and attachment counts

#### Scenario: Show missing generated Skill
- **WHEN** a user runs `skill-forge show <skill-name>` for a missing generated package
- **THEN** the command SHALL exit non-zero with a clear missing generated Skill message

### Requirement: Diff generated Skill files
The system SHALL provide a command that compares the `SKILL.md` files of two generated Skill packages.

#### Scenario: Diff two generated Skills
- **WHEN** a user runs `skill-forge diff <skill-a> <skill-b>`
- **THEN** the system SHALL display a unified diff of the two generated `SKILL.md` files

#### Scenario: Diff identical generated Skills
- **WHEN** the selected generated `SKILL.md` files have identical content
- **THEN** the system SHALL display a clear no-differences message and exit successfully

#### Scenario: Diff missing generated Skill
- **WHEN** either named generated Skill package does not exist
- **THEN** the command SHALL exit non-zero with a clear missing generated Skill message

### Requirement: Skill library management is covered by automated tests
The system SHALL include automated tests for listing, showing, and diffing generated Skill packages.

#### Scenario: Tests cover library commands
- **WHEN** the test suite runs
- **THEN** it SHALL verify list, empty list, show, missing show, diff, no-difference diff, and missing diff behavior

### Requirement: Library inspection exposes generation provenance
The system SHALL expose generation provenance metadata for generated Skill packages when `skill-forge.json` exists.

#### Scenario: Show generated Skill with provenance
- **WHEN** a user runs `skill-forge show <skill-name>` for a package containing `skill-forge.json`
- **THEN** the command SHALL display provenance fields including blueprint, LLM usage, quality, and generated timestamp

#### Scenario: Show generated Skill without provenance
- **WHEN** a user runs `skill-forge show <skill-name>` for a package without `skill-forge.json`
- **THEN** the command SHALL still display existing package metadata and SHALL indicate missing provenance without failing

### Requirement: Library diff includes provenance differences
The system SHALL include provenance metadata differences when comparing generated Skill packages.

#### Scenario: Diff packages with different provenance
- **WHEN** a user runs `skill-forge diff <skill-a> <skill-b>` and the packages have different `skill-forge.json` content
- **THEN** the command SHALL display metadata differences in addition to `SKILL.md` differences

#### Scenario: Diff old package without provenance
- **WHEN** a user runs `skill-forge diff <skill-a> <skill-b>` and one package lacks `skill-forge.json`
- **THEN** the command SHALL still compare `SKILL.md` and SHALL report the metadata file difference

### Requirement: Library inspection shows eval summary
The system SHALL display the latest eval summary for a generated Skill package when an eval report exists.

#### Scenario: Show generated Skill with eval summary
- **WHEN** a user runs `skill-forge show <skill-name>` for a package containing `eval-report.json`
- **THEN** the command SHALL display total, passed, and failed eval counts

#### Scenario: Show generated Skill without eval summary
- **WHEN** a user runs `skill-forge show <skill-name>` for a package without `eval-report.json`
- **THEN** the command SHALL continue to display generated Skill metadata without failing

### Requirement: Upgrade candidates are library packages
The system SHALL manage upgrade candidate packages as generated Skill library packages.

#### Scenario: List upgrade candidate
- **WHEN** an upgrade candidate package exists in the generated Skill output directory
- **THEN** `skill-forge list` SHALL display it as a generated Skill package

#### Scenario: Show upgrade candidate
- **WHEN** a user runs `skill-forge show <candidate-name>` for an upgrade candidate package
- **THEN** the command SHALL display the candidate package metadata and provenance like any other generated Skill package

#### Scenario: Diff source and upgrade candidate
- **WHEN** a user runs `skill-forge diff <source-skill> <candidate-name>`
- **THEN** the command SHALL compare the source and candidate packages using the existing generated Skill diff behavior

