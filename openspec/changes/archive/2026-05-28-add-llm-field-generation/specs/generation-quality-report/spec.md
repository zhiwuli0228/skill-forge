## ADDED Requirements

### Requirement: Quality reports include content quality metrics
The generation quality report SHALL include deterministic content quality metrics for generated Skill content when the relevant sections are available.

#### Scenario: Report includes minimum content quality metrics
- **WHEN** `skill-forge create "<requirement>"` generates a Skill package with workflow, constraints, and quality gates
- **THEN** the quality report SHALL include workflow specificity, constraint verifiability, and quality gate clarity metrics

#### Scenario: Content quality metrics are deterministic
- **WHEN** the same generated Skill content is evaluated multiple times
- **THEN** the content quality metrics SHALL be identical

#### Scenario: Content quality metrics do not change validation status
- **WHEN** content quality metrics are low but post-generation validation has no errors
- **THEN** the quality report SHALL preserve the validation-derived status

#### Scenario: LLM and deterministic generations can be compared
- **WHEN** the same requirement is generated with and without `--llm`
- **THEN** the system SHALL expose content quality metrics for both generated packages so their workflow, constraint, and quality gate quality can be compared
