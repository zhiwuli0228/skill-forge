## ADDED Requirements

### Requirement: Create can use custom blueprints
The system SHALL allow explicit blueprint selection during Skill generation to use built-in, user-level, or project-level blueprints that are in scope for the command.

#### Scenario: Create with user custom blueprint
- **WHEN** a user runs `skill-forge create "<requirement>" --blueprint <custom-id>` and `<custom-id>` exists in the user blueprint root
- **THEN** the system SHALL apply that custom blueprint before rendering the Skill package

#### Scenario: Create with project custom blueprint
- **WHEN** a user runs `skill-forge create "<requirement>" --project <path> --blueprint <custom-id>` and `<custom-id>` exists in `<path>/.skill-forge/blueprints`
- **THEN** the system SHALL apply that project custom blueprint before rendering the Skill package

#### Scenario: Create without custom blueprints preserves built-in behavior
- **WHEN** a user runs `skill-forge create "<requirement>"` without custom blueprint roots containing matching blueprints
- **THEN** the system SHALL preserve the existing built-in blueprint matching and fallback behavior

#### Scenario: Duplicate custom blueprint IDs fail generation clearly
- **WHEN** `skill-forge create "<requirement>" --blueprint <id>` loads multiple in-scope blueprints with ID `<id>`
- **THEN** the system SHALL exit non-zero with a clear duplicate blueprint ID message
