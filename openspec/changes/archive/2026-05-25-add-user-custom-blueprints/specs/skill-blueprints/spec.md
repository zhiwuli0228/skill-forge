## ADDED Requirements

### Requirement: User and project Skill blueprints are loadable
The system SHALL load Skill blueprints from built-in, user-level, and project-level blueprint roots when those roots are in scope.

#### Scenario: Load user custom blueprints
- **WHEN** the blueprint loader is invoked with a user blueprint root containing a valid blueprint YAML file
- **THEN** it SHALL return the custom blueprint together with the built-in blueprints

#### Scenario: Load project custom blueprints
- **WHEN** the blueprint loader is invoked with a project blueprint root containing a valid blueprint YAML file
- **THEN** it SHALL return the project blueprint together with other in-scope blueprints

#### Scenario: Ignore missing custom blueprint directories
- **WHEN** the user or project blueprint root does not exist
- **THEN** blueprint loading SHALL continue using the remaining in-scope roots without failing

#### Scenario: Reject duplicate IDs across roots
- **WHEN** two in-scope blueprint files define the same blueprint ID
- **THEN** blueprint loading SHALL fail with a clear duplicate ID error that identifies the duplicate blueprint ID

### Requirement: Blueprint source metadata is exposed
The system SHALL expose source metadata for each loaded blueprint so users can distinguish built-in, user-level, and project-level blueprints.

#### Scenario: List blueprints with source
- **WHEN** the user runs `skill-forge blueprints list`
- **THEN** the CLI SHALL display each blueprint ID, name, task type, description, and source

#### Scenario: Show blueprint with source path
- **WHEN** the user runs `skill-forge blueprints show <blueprint-id>`
- **THEN** the CLI SHALL display the selected blueprint details, source, and file path

#### Scenario: Preserve built-in source metadata
- **WHEN** built-in blueprints are loaded
- **THEN** each built-in blueprint SHALL be exposed with source `builtin`
