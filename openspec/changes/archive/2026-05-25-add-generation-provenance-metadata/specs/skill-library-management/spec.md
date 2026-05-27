## ADDED Requirements

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
