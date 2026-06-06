# skill-adoption-workflow Specification

## Purpose
Define how Skill Forge adopts cached community Skill documents from the local research corpus into the managed Skill library, providing a trust-preserving import workflow that does not fetch remote content or automatically modify adopted content.

## Requirements
### Requirement: Adopt cached corpus Skill documents
The system SHALL provide an adoption workflow that creates a local managed Skill package from a cached corpus document.

#### Scenario: Adopt by document ID
- **WHEN** a user runs `skill-forge adopt --document-id <id>` for a cached corpus document containing Skill content
- **THEN** the system SHALL create a local Skill package in the configured output directory

#### Scenario: Missing document ID
- **WHEN** a user runs `skill-forge adopt --document-id <id>` and no cached corpus document exists for that ID
- **THEN** the command SHALL exit non-zero with a clear missing corpus document message

#### Scenario: Adopt does not fetch remote content
- **WHEN** a user runs `skill-forge adopt --document-id <id>`
- **THEN** the system SHALL read from the local corpus cache and SHALL NOT fetch remote source content

### Requirement: Adopted packages preserve source Skill content
The adoption workflow SHALL write the cached Skill content to `SKILL.md` without applying generation templates, blueprints, or automatic content repair.

#### Scenario: Adopt writes cached content
- **WHEN** a corpus document contains cached `SKILL.md` content
- **THEN** the adopted package SHALL contain a `SKILL.md` file with that content preserved

#### Scenario: Name override does not rewrite content
- **WHEN** a user adopts a Skill with an explicit `--name <package-name>` option
- **THEN** the system SHALL use the provided package name for the output directory and SHALL NOT rewrite the adopted `SKILL.md` frontmatter

### Requirement: Adoption package naming is deterministic
The adoption workflow SHALL derive a package name deterministically and protect existing packages from accidental overwrite.

#### Scenario: Derive package name from frontmatter
- **WHEN** an adopted Skill has frontmatter `name`
- **THEN** the system SHALL use that name as the default output package name

#### Scenario: Derive fallback package name
- **WHEN** an adopted Skill lacks frontmatter `name` but has a corpus title
- **THEN** the system SHALL derive a slug package name from the corpus title

#### Scenario: Package conflict fails
- **WHEN** the target package directory already exists
- **THEN** adoption SHALL exit non-zero with a clear package conflict message

### Requirement: Adopted packages include adoption provenance
The adoption workflow SHALL write provenance metadata that identifies the package as adopted from the local corpus.

#### Scenario: Write adoption provenance
- **WHEN** adoption succeeds
- **THEN** the package SHALL contain `skill-forge.json` with origin type, adoption timestamp, source name, corpus document ID, optional example ID, platform when known, and content hash when known

#### Scenario: Provenance includes source URL when available
- **WHEN** the corpus document has a source or document URL available
- **THEN** adoption provenance SHALL include that URL

### Requirement: Adoption runs quality checks
The adoption workflow SHALL run existing validation and quality reporting after writing the adopted package.

#### Scenario: Adopted valid Skill reports quality
- **WHEN** adoption writes a package with a valid `SKILL.md`
- **THEN** the command SHALL display validation status and quality report output

#### Scenario: Adopted Skill with warnings reports suggestions
- **WHEN** adoption writes a package that produces validation warnings
- **THEN** the command SHALL display deterministic repair suggestions for those warnings without automatically modifying the package

#### Scenario: Adopted invalid Skill reports errors
- **WHEN** adoption writes a package that produces validation errors
- **THEN** the command SHALL display validation errors and deterministic repair suggestions

### Requirement: Adoption is covered by automated tests
The system SHALL include automated tests for adoption service and CLI behavior.

#### Scenario: Tests cover adoption workflow
- **WHEN** the test suite runs
- **THEN** it SHALL verify successful adoption, missing document rejection, package conflict detection, name override, provenance writing, validation integration, and CLI integration
