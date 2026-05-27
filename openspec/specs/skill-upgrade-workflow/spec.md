# skill-upgrade-workflow Specification

## Purpose
Define deterministic upgrade candidate generation for existing generated Skill packages using provenance metadata and current blueprint standards. This capability lets users regenerate a candidate package, validate its quality, and compare it with the source package without overwriting the original Skill.
## Requirements
### Requirement: Upgrade command generates candidate packages
The system SHALL provide an upgrade command that generates a new candidate package from an existing generated Skill package.

#### Scenario: Upgrade existing Skill with provenance
- **WHEN** a user runs `skill-forge upgrade <skill-name>` for a generated package containing valid provenance metadata
- **THEN** the system SHALL generate an upgrade candidate package without modifying the source package

#### Scenario: Candidate uses default upgraded name
- **WHEN** a user runs `skill-forge upgrade <skill-name>` without a candidate name
- **THEN** the system SHALL write the candidate as `<skill-name>-upgraded`

#### Scenario: Candidate name can be overridden
- **WHEN** a user runs `skill-forge upgrade <skill-name> --candidate-name <name>`
- **THEN** the system SHALL write the candidate package using the provided candidate name

### Requirement: Upgrade requires provenance metadata
The system SHALL require `skill-forge.json` provenance metadata before upgrading a generated Skill package.

#### Scenario: Missing provenance blocks upgrade
- **WHEN** a user runs `skill-forge upgrade <skill-name>` for a package without provenance metadata
- **THEN** the command SHALL exit non-zero with a clear missing provenance message

#### Scenario: Invalid provenance blocks upgrade
- **WHEN** a user runs `skill-forge upgrade <skill-name>` for a package with unreadable or invalid provenance metadata
- **THEN** the command SHALL exit non-zero with a clear invalid provenance message

### Requirement: Upgrade reapplies recorded blueprint standards
The system SHALL reapply the current version of the blueprint recorded in provenance metadata when generating an upgrade candidate.

#### Scenario: Recorded blueprint is available
- **WHEN** provenance metadata records a blueprint ID that can be loaded
- **THEN** the upgrade candidate SHALL be generated using that current blueprint

#### Scenario: Recorded blueprint is missing
- **WHEN** provenance metadata records a blueprint ID that cannot be loaded
- **THEN** the command SHALL exit non-zero with a clear missing blueprint message

### Requirement: Upgrade validates candidate quality
The system SHALL validate the generated upgrade candidate and report old and new quality scores.

#### Scenario: Candidate quality is reported
- **WHEN** an upgrade candidate is generated
- **THEN** the command SHALL display the previous quality score from provenance and the candidate validation quality score

#### Scenario: Invalid candidate fails upgrade
- **WHEN** the generated candidate fails validation
- **THEN** the command SHALL report the validation errors and exit non-zero

### Requirement: Upgrade protects existing packages
The system SHALL avoid overwriting existing candidate packages unless explicitly requested.

#### Scenario: Candidate already exists
- **WHEN** a user runs `skill-forge upgrade <skill-name>` and the target candidate package already exists
- **THEN** the command SHALL exit non-zero and SHALL NOT overwrite the candidate package

#### Scenario: Force replaces existing candidate
- **WHEN** a user runs `skill-forge upgrade <skill-name> --force` and the target candidate package already exists
- **THEN** the system SHALL replace only the candidate package and SHALL NOT modify the source package
