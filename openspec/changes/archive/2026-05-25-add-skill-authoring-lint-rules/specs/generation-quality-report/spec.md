## ADDED Requirements

### Requirement: Quality reports include authoring lint warnings
The generation quality report SHALL include authoring lint warnings returned by validation and SHALL apply the existing warning penalty model to them.

#### Scenario: Lint warning reduces generated quality score
- **WHEN** post-generation validation returns authoring lint warnings and no errors
- **THEN** the quality report SHALL include those warnings and reduce the quality score deterministically

#### Scenario: Lint warnings do not fail generation
- **WHEN** post-generation validation returns only authoring lint warnings
- **THEN** non-interactive `create` SHALL complete successfully with a valid-with-warnings quality status
