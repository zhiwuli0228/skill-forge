## ADDED Requirements

### Requirement: Validation results support quality reporting
The system SHALL support constructing generation quality reports from structured validation results without changing existing validation rule semantics.

#### Scenario: Build report from validation result
- **WHEN** a validation result contains aggregate status, errors, and warnings
- **THEN** the system SHALL be able to derive a quality score, status label, issue lists, and next actions from that result

#### Scenario: Existing validate command remains compatible
- **WHEN** a user runs `skill-forge validate <skill-path>`
- **THEN** the command SHALL continue to report validation errors separately from warnings and return non-zero only for validation errors
