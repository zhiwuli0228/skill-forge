## ADDED Requirements

### Requirement: LLM-assisted reference lookup can prefer promoted Skills
The system SHALL allow LLM-assisted local reference lookup to prefer
promoted Skills when high-quality local references are available.

#### Scenario: Promoted reference is selected
- **WHEN** local reference lookup finds both promoted and non-promoted
  Skills that satisfy the same relevance and quality gates
- **THEN** the system SHALL prefer the promoted Skill as a reference
  candidate

#### Scenario: Promotion does not bypass quality gates
- **WHEN** a promoted Skill fails the existing relevance or content
  quality thresholds
- **THEN** the system SHALL NOT use promotion alone to force that Skill
  into the LLM-assisted reference context

#### Scenario: No promoted references remains valid
- **WHEN** local reference lookup finds no promoted Skills
- **THEN** the system SHALL preserve the existing reference-selection
  behavior
