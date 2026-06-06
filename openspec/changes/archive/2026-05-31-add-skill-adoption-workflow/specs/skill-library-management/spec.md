## ADDED Requirements

### Requirement: Adopted Skills are library packages
The system SHALL manage adopted Skill packages through the existing generated Skill library commands.

#### Scenario: List adopted package
- **WHEN** an adopted Skill package exists in the configured output directory
- **THEN** `skill-forge list` SHALL display it as a library package

#### Scenario: Show adopted package
- **WHEN** a user runs `skill-forge show <skill-name>` for an adopted package
- **THEN** the command SHALL display the package metadata and adoption provenance

#### Scenario: Diff adopted package
- **WHEN** a user runs `skill-forge diff <adopted-skill> <other-skill>`
- **THEN** the command SHALL compare the adopted package using existing library diff behavior

### Requirement: Library inspection exposes adoption provenance
The system SHALL display adoption provenance for packages whose `skill-forge.json` identifies an adopted origin.

#### Scenario: Show adoption source
- **WHEN** a user runs `skill-forge show <skill-name>` for an adopted package
- **THEN** the command SHALL display the adoption origin, source name, corpus document ID, and adoption timestamp when available

#### Scenario: Show adoption platform
- **WHEN** an adopted package provenance includes platform metadata
- **THEN** the command SHALL display that platform metadata with the package details

#### Scenario: Legacy generated package remains compatible
- **WHEN** a user runs `skill-forge show <skill-name>` for a generated package without adoption provenance
- **THEN** the command SHALL preserve existing generated package display behavior
