## ADDED Requirements

### Requirement: Validate command reports Skill package validity
The system SHALL provide a `validate <skill-path>` command that checks a Skill package and reports validation errors separately from warnings.

#### Scenario: Valid generated package passes validation
- **WHEN** a user runs `skill-forge validate <skill-path>` against a generated package containing a valid `SKILL.md`
- **THEN** the command SHALL complete successfully and report that the package is valid

#### Scenario: Validation failure returns non-zero
- **WHEN** a user runs `skill-forge validate <skill-path>` against an invalid package
- **THEN** the command SHALL return a non-zero exit code and display validation errors

### Requirement: Validator checks required Skill package elements
The validator SHALL treat missing required package elements as errors.

#### Scenario: Missing Skill directory is an error
- **WHEN** validation receives a path that does not exist or is not a directory
- **THEN** the result SHALL include an error for the missing Skill directory

#### Scenario: Missing SKILL.md is an error
- **WHEN** validation receives a Skill directory without `SKILL.md`
- **THEN** the result SHALL include an error for missing `SKILL.md`

#### Scenario: Missing frontmatter fields are errors
- **WHEN** `SKILL.md` lacks frontmatter, `name`, or `description`
- **THEN** the result SHALL include errors for the missing required metadata

### Requirement: Validator warns for recommended Skill sections
The validator SHALL report warnings for missing recommended sections without making the package invalid.

#### Scenario: Missing recommended sections are warnings
- **WHEN** `SKILL.md` lacks recommended sections such as Purpose, When to use, When not to use, Workflow, Output format, or Quality gates
- **THEN** the result SHALL include warnings for the missing sections while keeping validation successful if there are no errors

### Requirement: Validation result is structured
The system SHALL represent validation output with structured issues and aggregate status.

#### Scenario: ValidationResult separates errors and warnings
- **WHEN** validation completes
- **THEN** the result SHALL include `ok`, `errors`, and `warnings` fields, with each issue carrying level, code, and message

### Requirement: Skill validation is covered by automated tests
The system SHALL include automated tests for validation behavior.

#### Scenario: Tests cover valid and invalid packages
- **WHEN** the test suite runs
- **THEN** it SHALL verify valid package success, missing directory errors, missing `SKILL.md` errors, missing frontmatter errors, recommended section warnings, and CLI exit behavior
