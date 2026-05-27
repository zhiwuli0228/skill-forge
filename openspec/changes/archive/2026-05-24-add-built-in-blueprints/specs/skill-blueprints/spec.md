## MODIFIED Requirements

### Requirement: Built-in Skill blueprints are loadable
The system SHALL load built-in Skill blueprints from repository-owned YAML files using a deterministic order.

#### Scenario: Load built-in blueprints
- **WHEN** the blueprint loader is invoked
- **THEN** it returns all valid built-in blueprints sorted by blueprint ID

#### Scenario: Reject duplicate blueprint IDs
- **WHEN** multiple blueprint files define the same blueprint ID
- **THEN** the loader fails with a clear duplicate ID error

#### Scenario: Includes first high-value blueprint set
- **WHEN** the blueprint loader is invoked
- **THEN** it returns built-in blueprints for `bug-investigation`, `code-review`, `test-generation`, and `openspec-change`

### Requirement: Users can list built-in blueprints
The system SHALL provide a CLI command that lists built-in Skill blueprints.

#### Scenario: List blueprints
- **WHEN** the user runs `skill-forge blueprints list`
- **THEN** the CLI displays each blueprint ID, name, task type, and description

#### Scenario: List expanded built-in blueprint set
- **WHEN** the user runs `skill-forge blueprints list`
- **THEN** the CLI output includes `code-review`, `test-generation`, and `openspec-change`

### Requirement: Users can inspect a built-in blueprint
The system SHALL provide a CLI command that displays the details of a single built-in Skill blueprint.

#### Scenario: Show existing blueprint
- **WHEN** the user runs `skill-forge blueprints show bug-investigation`
- **THEN** the CLI displays the blueprint metadata and section defaults

#### Scenario: Show missing blueprint
- **WHEN** the user runs `skill-forge blueprints show missing-blueprint`
- **THEN** the CLI exits non-zero and displays a clear not found message

#### Scenario: Show expanded blueprint details
- **WHEN** the user runs `skill-forge blueprints show code-review`
- **THEN** the CLI displays task-specific workflow, outputs, and quality gates for code review
