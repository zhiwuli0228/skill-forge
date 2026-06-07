# experience-accumulation Specification

## Purpose
TBD - created by archiving change add-experience-accumulation. Update Purpose after archive.
## Requirements
### Requirement: Experience rules are stored locally
The system SHALL store derived experience rules under the Skill Forge home directory in a local experience store.

#### Scenario: Experience directory stores rules
- **WHEN** experience rules are derived
- **THEN** the system SHALL write structured rule records under `~/.skill-forge/experience/`
- **AND** each rule record SHALL include a stable rule ID, task type scope, rule text, priority, derivation timestamp, and evidence references

#### Scenario: Empty experience store is valid
- **WHEN** the experience directory is missing or contains no rules
- **THEN** generation SHALL continue with the no-experience baseline

#### Scenario: Clearing experience restores baseline
- **WHEN** the user clears the experience directory
- **THEN** future generation SHALL behave as if no experience rules exist

### Requirement: Experience rules are derived from local evidence
The system SHALL derive experience rules from persisted local eval reports, generation provenance, task type metadata, and deterministic content quality metrics.

#### Scenario: Eval failures produce candidate rules
- **WHEN** multiple generated packages for the same task type have repeated eval assertion failures
- **THEN** the system SHALL derive candidate rules that target those repeated failure patterns
- **AND** each candidate rule SHALL reference the source packages and eval cases that produced the evidence

#### Scenario: Low content quality produces candidate rules
- **WHEN** generated packages for the same task type repeatedly score low on workflow specificity, constraint verifiability, or quality gate clarity
- **THEN** the system SHALL derive candidate rules that target the low-scoring content dimension

#### Scenario: Insufficient samples skip derivation
- **WHEN** the local sample set is below the configured minimum sample threshold
- **THEN** the system SHALL skip rule derivation without error

### Requirement: Experience derivation is deterministic and local
The system SHALL derive experience rules without calling an LLM, remote service, or network dependency.

#### Scenario: Derivation runs offline
- **WHEN** experience derivation runs
- **THEN** the system SHALL use only local generated package metadata, eval reports, and content quality data
- **AND** it SHALL NOT require network access

#### Scenario: Same evidence produces same rules
- **WHEN** the same local evidence set is processed multiple times
- **THEN** the derived rule IDs and rule content SHALL be stable

### Requirement: Experience rules are explainable
The system SHALL preserve evidence references for each experience rule so users can inspect why a rule exists.

#### Scenario: Rule includes evidence references
- **WHEN** an experience rule is stored
- **THEN** it SHALL include references to source generated package names, eval case IDs when available, and the quality dimensions that contributed to the rule

#### Scenario: Rule evidence avoids full Skill copies
- **WHEN** an experience rule stores evidence
- **THEN** it SHALL store compact references and summary signals rather than copying complete generated Skill content

### Requirement: Applicable experience rules are selected for generation
The system SHALL select applicable experience rules by task type, language, target platform, and rule priority before generation.

#### Scenario: Matching rules are selected
- **WHEN** generation starts for a requirement with a task type that matches stored experience rules
- **THEN** the system SHALL select applicable rules for that task type

#### Scenario: Nonmatching rules are ignored
- **WHEN** stored experience rules target a different task type, language, or platform than the current generation request
- **THEN** those rules SHALL NOT be applied to the current generation

#### Scenario: Conflicting rules are resolved deterministically
- **WHEN** multiple applicable rules conflict
- **THEN** the system SHALL choose rules by specificity and priority using a deterministic ordering

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

