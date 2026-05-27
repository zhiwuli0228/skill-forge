## ADDED Requirements

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
