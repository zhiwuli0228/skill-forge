## ADDED Requirements

### Requirement: Adoption reuses validation output
The adoption workflow SHALL reuse existing Skill validation result semantics after writing an adopted package.

#### Scenario: Adoption validates written package
- **WHEN** adoption writes a local Skill package
- **THEN** the system SHALL validate the written package using the existing Skill validator

#### Scenario: Adoption validation errors are non-zero
- **WHEN** the adopted package has validation errors
- **THEN** the adoption command SHALL exit non-zero and display those validation errors

#### Scenario: Adoption validation warnings do not fail
- **WHEN** the adopted package has validation warnings and no validation errors
- **THEN** the adoption command SHALL complete successfully and display those warnings

### Requirement: Adoption displays repair suggestions
The adoption workflow SHALL display deterministic repair suggestions for validation issues found after adoption.

#### Scenario: Adoption displays warning suggestions
- **WHEN** adoption validation reports warnings
- **THEN** the command SHALL display deterministic repair suggestions associated with those warnings

#### Scenario: Adoption displays error suggestions
- **WHEN** adoption validation reports errors
- **THEN** the command SHALL display deterministic repair suggestions associated with those errors

#### Scenario: Adoption omits empty suggestions
- **WHEN** adoption validation reports no errors and no warnings
- **THEN** the command SHALL NOT display an empty suggestions section
