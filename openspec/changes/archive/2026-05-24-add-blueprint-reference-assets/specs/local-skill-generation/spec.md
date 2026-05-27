## ADDED Requirements

### Requirement: Blueprint-declared files are generated
The system SHALL write blueprint-declared references, assets, and scripts into generated Skill packages when the applied blueprint declares them.

#### Scenario: Generate blueprint-declared reference
- **WHEN** a user creates a Skill using a blueprint that declares `references/diagnosis-checklist.md`
- **THEN** the generated Skill package SHALL include `references/diagnosis-checklist.md` with the declared content

#### Scenario: Generate single-file package without declarations
- **WHEN** a user creates a Skill using a blueprint that declares no references, assets, or scripts
- **THEN** the generated Skill package SHALL contain `SKILL.md` and no generated attachment files

#### Scenario: Generated package metadata includes attachments
- **WHEN** the generator writes blueprint-declared files
- **THEN** the returned package metadata SHALL include the generated attachment paths grouped by references, assets, or scripts

### Requirement: Generated attachment paths remain inside package
The system SHALL prevent blueprint-declared files from being written outside the generated Skill package directory.

#### Scenario: Reject path traversal during generation
- **WHEN** generation receives a declared file path that resolves outside the package directory
- **THEN** generation SHALL fail before writing that file outside the package
