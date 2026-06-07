## ADDED Requirements

### Requirement: Library inspection exposes collection state
The system SHALL display governed collection metadata for local library
Skills when collection records exist.

#### Scenario: Show collection state
- **WHEN** a user runs `skill-forge show <skill-name>` for a Skill with
  collection metadata
- **THEN** the command SHALL display the collection state and score
  summary

#### Scenario: Missing collection metadata is allowed
- **WHEN** a library Skill has no collection record
- **THEN** the command SHALL preserve existing package display behavior
  and indicate that no collection state is recorded

### Requirement: Library list can expose promoted Skills
The system SHALL allow the library view to identify promoted or curated
Skills.

#### Scenario: List promoted Skill
- **WHEN** a promoted Skill exists in the library
- **THEN** `skill-forge list` SHALL expose that promoted state in the
  displayed metadata or equivalent output mode

#### Scenario: Curated and promoted states remain distinct
- **WHEN** multiple library Skills have different collection states
- **THEN** the library display SHALL preserve those distinctions rather
  than collapsing them into one generic label
