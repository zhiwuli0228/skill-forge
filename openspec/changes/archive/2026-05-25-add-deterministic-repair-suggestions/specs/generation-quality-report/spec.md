## ADDED Requirements

### Requirement: Quality reports include repair suggestions
The generation quality report SHALL include deterministic repair suggestions derived from validation errors and warnings.

#### Scenario: Create displays suggestions for generated warnings
- **WHEN** non-interactive `create` generates a package with validation warnings
- **THEN** the quality report output SHALL display repair suggestions for those warnings

#### Scenario: Create displays suggestions for generated errors
- **WHEN** non-interactive `create` generates a package with validation errors
- **THEN** the quality report output SHALL display repair suggestions for those errors before exiting non-zero

#### Scenario: Clean quality report omits suggestions
- **WHEN** non-interactive `create` generates a package with no validation issues
- **THEN** the quality report output SHALL NOT display an empty suggestions section
