## ADDED Requirements

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
