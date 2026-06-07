## ADDED Requirements

### Requirement: Experience derivation can prefer curated evidence
The experience system SHALL be able to prefer curated or promoted local
Skills as stronger evidence inputs when deriving reusable rules.

#### Scenario: Promoted evidence is preferred
- **WHEN** multiple local Skills are available as evidence candidates and
  some are promoted
- **THEN** the derivation flow SHALL be able to prioritize promoted
  Skills where that does not conflict with deterministic evidence rules

#### Scenario: No curated evidence remains valid
- **WHEN** no curated or promoted Skills are available
- **THEN** experience derivation SHALL continue using the existing local
  evidence baseline without failing
