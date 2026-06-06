# skill-evaluation Specification

## Purpose
Define deterministic local Skill eval cases, static assertion execution, batch eval behavior, and persisted eval reports for generated Skill packages. This capability lets users encode team-specific task expectations without executing an Agent, running code, calling an LLM, or depending on a remote eval service.
## Requirements
### Requirement: Eval case files are loadable
The system SHALL load deterministic Skill eval cases from YAML files.

#### Scenario: Load valid eval case
- **WHEN** an eval case file contains an ID, target skill name, optional input request, and assertions
- **THEN** the system SHALL parse it into a structured eval case

#### Scenario: Reject invalid eval case
- **WHEN** an eval case file is missing required fields or has invalid assertion data
- **THEN** eval execution SHALL fail with a clear eval case error

### Requirement: Single eval case can run against a generated Skill
The system SHALL provide a CLI command that runs one eval case against a generated Skill package.

#### Scenario: Eval case passes
- **WHEN** a user runs `skill-forge eval <skill-name> --case <file>` and all assertions pass
- **THEN** the command SHALL report the eval as passed and exit successfully

#### Scenario: Eval case fails
- **WHEN** a user runs `skill-forge eval <skill-name> --case <file>` and one or more assertions fail
- **THEN** the command SHALL report each failed assertion and exit non-zero

#### Scenario: Eval missing generated Skill
- **WHEN** a user runs `skill-forge eval <skill-name> --case <file>` for a missing generated Skill
- **THEN** the command SHALL exit non-zero with a clear missing generated Skill message

### Requirement: Batch eval cases can run from a directory
The system SHALL run all `.yaml` and `.yml` eval case files from a directory in deterministic order.

#### Scenario: Batch eval summary
- **WHEN** a user runs `skill-forge eval <skill-name> --cases <dir>`
- **THEN** the command SHALL run each eval case file and display total, passed, and failed counts

### Requirement: Static eval assertions are supported
The system SHALL support deterministic static assertions over generated Skill content.

#### Scenario: Required sections assertion
- **WHEN** an eval case lists required sections
- **THEN** evaluation SHALL pass only if each required section appears in the Skill content

#### Scenario: Required constraints assertion
- **WHEN** an eval case lists required constraints
- **THEN** evaluation SHALL pass only if each required constraint appears in the Skill content

#### Scenario: Forbidden phrases assertion
- **WHEN** an eval case lists forbidden phrases
- **THEN** evaluation SHALL fail if any forbidden phrase appears in the Skill content

### Requirement: Eval reports are persisted
The system SHALL write the latest eval report into the evaluated Skill package.

#### Scenario: Persist latest eval report
- **WHEN** eval execution completes
- **THEN** the system SHALL write an `eval-report.json` file containing case results and summary counts

### Requirement: Eval reports can feed experience derivation
The system SHALL make persisted eval reports available as local evidence for experience rule derivation.

#### Scenario: Failed assertions are available as evidence
- **WHEN** an eval report contains failed assertions for a generated Skill package
- **THEN** experience derivation SHALL be able to read the failed assertion names, messages, case IDs, and package name as evidence

#### Scenario: Passing eval reports do not create failure rules
- **WHEN** an eval report contains no failed assertions
- **THEN** experience derivation SHALL NOT derive failure-pattern rules from that report

#### Scenario: Missing eval reports are skipped
- **WHEN** a generated Skill package has no persisted eval report
- **THEN** experience derivation SHALL skip eval evidence for that package without failing

