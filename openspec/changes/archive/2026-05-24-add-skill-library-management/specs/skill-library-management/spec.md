## ADDED Requirements

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
