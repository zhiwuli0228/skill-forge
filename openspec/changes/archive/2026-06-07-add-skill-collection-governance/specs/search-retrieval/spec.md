## ADDED Requirements

### Requirement: Search can filter by collection state
The search command SHALL allow users to filter local results by governed
collection state.

#### Scenario: Filter to promoted Skills
- **WHEN** a user runs a search with a promoted-only collection filter
- **THEN** the system SHALL return only promoted Skills when such Skills
  exist

#### Scenario: Empty filtered result is clear
- **WHEN** a collection filter removes all candidates
- **THEN** the system SHALL display a clear empty-result message without
  implying corpus failure

### Requirement: Search can prefer promoted Skills
The search command SHALL be able to prefer promoted Skills over ordinary
library entries when other retrieval signals are similar.

#### Scenario: Promotion boosts ranking
- **WHEN** two results are similarly relevant and one is promoted
- **THEN** the promoted result SHALL receive a deterministic ranking
  advantage

#### Scenario: Default ranking remains compatible
- **WHEN** a user runs the default search command without collection
  options
- **THEN** the command SHALL preserve its existing output contract and
  SHALL NOT require collection metadata to be present
