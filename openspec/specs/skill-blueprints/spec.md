# skill-blueprints Specification

## Purpose
Define how Skill Forge exposes built-in Skill blueprints as deterministic, validated, inspectable configuration data for future blueprint-backed Skill generation.
## Requirements
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

### Requirement: Blueprint inspection does not alter Skill generation
The system SHALL NOT change existing Skill generation behavior when built-in blueprints are introduced.

#### Scenario: Existing create behavior remains available
- **WHEN** the user runs `skill-forge create "Java 存量代码 bug 定位 skill"`
- **THEN** the command generates a Skill package through the existing generation path

### Requirement: Blueprints can be matched for generation
The system SHALL allow generation code to find a built-in Skill blueprint by task type and SHALL allow generation code to load a built-in Skill blueprint by explicit blueprint ID.

#### Scenario: Match blueprint by task type
- **WHEN** generation requests a blueprint for task type `bug-investigation`
- **THEN** the system returns the built-in `bug-investigation` blueprint

#### Scenario: No matching blueprint
- **WHEN** generation requests a blueprint for an unknown task type
- **THEN** the system reports no match without failing generation

#### Scenario: Select blueprint by ID
- **WHEN** generation requests a blueprint with ID `code-review`
- **THEN** the system returns the built-in `code-review` blueprint

#### Scenario: Missing blueprint by ID
- **WHEN** generation requests a blueprint with ID `missing-blueprint`
- **THEN** the system reports a clear not found error

### Requirement: Blueprint defaults can enrich requirements
The system SHALL merge matching or explicitly selected blueprint defaults into a `SkillRequirement` before rendering.

#### Scenario: Fill missing requirement lists
- **WHEN** a matching blueprint has defaults for a list field that is empty on the requirement
- **THEN** the system copies those defaults into the requirement

#### Scenario: Preserve existing requirement values
- **WHEN** the requirement already contains values for a field
- **THEN** the system preserves those values and appends non-duplicate blueprint defaults only where appropriate

#### Scenario: Enrich with explicitly selected blueprint
- **WHEN** a blueprint ID is explicitly selected for enrichment
- **THEN** the system merges that blueprint's defaults into the requirement regardless of the requirement task type

### Requirement: Blueprints can declare generated package files
The system SHALL allow built-in Skill blueprints to declare additional files for generated Skill packages.

#### Scenario: Blueprint declares a reference file
- **WHEN** a blueprint includes a reference file declaration
- **THEN** blueprint loading SHALL expose the declared relative path and content

#### Scenario: Blueprint declares no package files
- **WHEN** a blueprint does not include file declarations
- **THEN** blueprint loading SHALL still succeed and expose empty file declaration lists

#### Scenario: Blueprint rejects unsafe package file path
- **WHEN** a blueprint declares an absolute path or a path containing `..`
- **THEN** blueprint loading SHALL fail with a clear validation error

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

