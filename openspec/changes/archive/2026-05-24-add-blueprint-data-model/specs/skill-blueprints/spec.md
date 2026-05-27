## ADDED Requirements

### Requirement: Built-in Skill blueprints are loadable
The system SHALL load built-in Skill blueprints from repository-owned YAML files using a deterministic order.

#### Scenario: Load built-in blueprints
- **WHEN** the blueprint loader is invoked
- **THEN** it returns all valid built-in blueprints sorted by blueprint ID

#### Scenario: Reject duplicate blueprint IDs
- **WHEN** multiple blueprint files define the same blueprint ID
- **THEN** the loader fails with a clear duplicate ID error

### Requirement: Skill blueprints are validated
The system SHALL validate blueprint files before exposing them through the CLI.

#### Scenario: Reject missing required fields
- **WHEN** a blueprint file is missing a required field such as `id`, `name`, `description`, or `task_type`
- **THEN** blueprint loading fails with a clear validation error

#### Scenario: Reject unstable blueprint ID
- **WHEN** a blueprint ID is not a lowercase kebab-case slug
- **THEN** blueprint loading fails with a clear validation error

### Requirement: Users can list built-in blueprints
The system SHALL provide a CLI command that lists built-in Skill blueprints.

#### Scenario: List blueprints
- **WHEN** the user runs `skill-forge blueprints list`
- **THEN** the CLI displays each blueprint ID, name, task type, and description

### Requirement: Users can inspect a built-in blueprint
The system SHALL provide a CLI command that displays the details of a single built-in Skill blueprint.

#### Scenario: Show existing blueprint
- **WHEN** the user runs `skill-forge blueprints show bug-investigation`
- **THEN** the CLI displays the blueprint metadata and section defaults

#### Scenario: Show missing blueprint
- **WHEN** the user runs `skill-forge blueprints show missing-blueprint`
- **THEN** the CLI exits non-zero and displays a clear not found message

### Requirement: Blueprint inspection does not alter Skill generation
The system SHALL NOT change existing Skill generation behavior when built-in blueprints are introduced.

#### Scenario: Existing create behavior remains available
- **WHEN** the user runs `skill-forge create "Java 存量代码 bug 定位 skill"`
- **THEN** the command generates a Skill package through the existing generation path
