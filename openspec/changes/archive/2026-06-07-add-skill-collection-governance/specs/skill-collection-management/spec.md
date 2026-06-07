## ADDED Requirements

### Requirement: Local Skill collections are governed explicitly
The system SHALL provide a local collection layer for managed Skills that
is separate from discovery, adoption, and blueprint identity.

#### Scenario: Skill enters candidate collection state
- **WHEN** a generated or adopted Skill is first evaluated for
  collection
- **THEN** the system SHALL allow it to exist in a `candidate` state
  without treating it as curated or promoted

#### Scenario: Curated state is explicit
- **WHEN** a user or deterministic workflow marks a Skill as curated
- **THEN** the system SHALL record the curated state in the local
  collection store together with rationale metadata

#### Scenario: Promotion is explicit
- **WHEN** a Skill is promoted for preferred reuse
- **THEN** the system SHALL record a `promoted` state and SHALL preserve
  evidence references explaining that decision

### Requirement: Collection state is independent of origin
The system SHALL allow generated and adopted Skills to participate in
the same collection workflow without conflating origin with quality.

#### Scenario: Generated Skill is promoted
- **WHEN** a generated Skill satisfies promotion criteria
- **THEN** the system SHALL allow it to become promoted

#### Scenario: Adopted Skill is promoted
- **WHEN** an adopted Skill satisfies promotion criteria
- **THEN** the system SHALL allow it to become promoted without
  rewriting the adopted `SKILL.md` content

#### Scenario: Adopted Skill is not auto-promoted
- **WHEN** a Skill is adopted from the corpus
- **THEN** the system SHALL NOT automatically mark it curated or
  promoted only because it was adopted

### Requirement: Collection records are stored locally and inspectably
The system SHALL store collection records in a local inspectable store.

#### Scenario: Collection store exists
- **WHEN** collection records are created
- **THEN** the system SHALL write them under the Skill Forge local home
  or project-scoped collection root

#### Scenario: Missing store is handled
- **WHEN** the collection store does not yet exist
- **THEN** the system SHALL create it lazily or treat the empty store as
  a valid no-collection baseline

#### Scenario: Collection record includes rationale
- **WHEN** a collection record is written
- **THEN** the record SHALL include the collection state, score summary,
  and rationale or evidence references
