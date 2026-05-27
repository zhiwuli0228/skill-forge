# skill-validation Specification

## Purpose
TBD - created by archiving change add-validation-and-installation. Update Purpose after archive.
## Requirements
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

### Requirement: Skill package attachment paths are safe
The system SHALL report invalid Skill packages that contain unsafe attachment paths when attachment paths are supplied for validation.

#### Scenario: Validate safe generated attachments
- **WHEN** a generated Skill package contains reference files under the Skill package directory
- **THEN** validation SHALL continue to validate the package successfully when `SKILL.md` is valid

#### Scenario: Reject unsafe attachment path metadata
- **WHEN** validation is given an attachment path that is absolute or contains `..`
- **THEN** validation SHALL report an error for unsafe attachment path metadata

### Requirement: Validation results support quality reporting
The system SHALL support constructing generation quality reports from structured validation results without changing existing validation rule semantics.

#### Scenario: Build report from validation result
- **WHEN** a validation result contains aggregate status, errors, and warnings
- **THEN** the system SHALL be able to derive a quality score, status label, issue lists, and next actions from that result

#### Scenario: Existing validate command remains compatible
- **WHEN** a user runs `skill-forge validate <skill-path>`
- **THEN** the command SHALL continue to report validation errors separately from warnings and return non-zero only for validation errors

### Requirement: Validator reports authoring lint warnings
The validator SHALL report deterministic authoring lint findings as warnings without changing validation error semantics.

#### Scenario: Invalid name slug warns
- **WHEN** `SKILL.md` frontmatter contains a `name` that is not lowercase kebab-case
- **THEN** validation SHALL include a `name_not_slug` warning

#### Scenario: Package name mismatch warns
- **WHEN** the Skill package directory name differs from the frontmatter `name`
- **THEN** validation SHALL include a `package_name_mismatch` warning

#### Scenario: Weak description warns
- **WHEN** frontmatter `description` is present but too short or lacks trigger or exclusion guidance
- **THEN** validation SHALL include authoring warnings for the missing description qualities

#### Scenario: Empty recommended section warns
- **WHEN** a recommended section heading exists but its body has no meaningful content
- **THEN** validation SHALL include an `empty_section` warning

#### Scenario: Thin workflow or quality gates warn
- **WHEN** Workflow or Quality gates sections contain too few actionable items
- **THEN** validation SHALL include authoring warnings for the thin section

#### Scenario: Lint warnings do not invalidate package
- **WHEN** validation finds authoring lint warnings and no errors
- **THEN** validation SHALL keep `ok` true

### Requirement: Validation output includes deterministic repair suggestions
The system SHALL provide deterministic repair suggestions for validation errors and warnings with known issue codes.

#### Scenario: Validate displays suggestions for errors
- **WHEN** `skill-forge validate <skill-path>` reports validation errors
- **THEN** the CLI SHALL display repair suggestions associated with those errors

#### Scenario: Validate displays suggestions for warnings
- **WHEN** `skill-forge validate <skill-path>` reports validation warnings and no errors
- **THEN** the CLI SHALL display repair suggestions associated with those warnings without failing validation

#### Scenario: No suggestions when no issues
- **WHEN** validation reports no errors and no warnings
- **THEN** the CLI SHALL NOT display an empty suggestions section

#### Scenario: Suggestions are deterministic
- **WHEN** the same validation issue code is reported multiple times
- **THEN** the system SHALL produce the same repair suggestion text for that code

