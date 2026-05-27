# interactive-drafts Specification

## Purpose
TBD - created by archiving change add-interactive-drafts. Update Purpose after archive.
## Requirements
### Requirement: Interactive create starts a resumable draft
The system SHALL allow users to start an interactive Skill creation flow from an initial requirement string.

#### Scenario: Interactive create creates draft state
- **WHEN** a user runs `skill-forge create "Java bug 定位 skill" --interactive`
- **THEN** the system SHALL create a draft state with a unique draft id, analyzed requirement data, current step, status, and timestamps

#### Scenario: Interactive create saves progress after each step
- **WHEN** a user answers an interactive prompt
- **THEN** the system SHALL persist the updated draft state to `~/.skill-forge/drafts/<draft-id>.json`

### Requirement: Draft state is structured and recoverable
The system SHALL represent draft progress with structured `SkillDraftState` data.

#### Scenario: Draft JSON contains required fields
- **WHEN** a draft is saved
- **THEN** the JSON SHALL include draft id, requirement, current step, status, optional project path, optional project context summary, selected examples, created timestamp, and updated timestamp

#### Scenario: Draft can be loaded by id
- **WHEN** a draft id is provided
- **THEN** the system SHALL load the corresponding draft JSON from the drafts directory

### Requirement: Resume command continues incomplete drafts
The system SHALL provide a `resume <draft-id>` command that continues an existing interactive draft.

#### Scenario: Resume skips completed steps
- **WHEN** a user resumes a draft with completed fields
- **THEN** the wizard SHALL continue from the draft current step instead of repeating already completed steps

#### Scenario: Resume generates Skill from ready draft
- **WHEN** a resumed draft reaches ready-to-generate status
- **THEN** the system SHALL generate the Skill package using the existing local generator

#### Scenario: Missing draft id fails clearly
- **WHEN** a user runs `skill-forge resume <draft-id>` for a draft that does not exist
- **THEN** the command SHALL fail with a clear message and non-zero exit code

### Requirement: Interactive wizard refines analyzed requirements
The wizard SHALL confirm and refine high-value `SkillRequirement` fields before generation.

#### Scenario: Wizard can update key fields
- **WHEN** the user edits fields such as name, usage boundaries, workflow, expected outputs, or quality gates
- **THEN** the draft requirement SHALL be updated before generation

#### Scenario: Wizard reuses existing generator
- **WHEN** interactive refinement is complete
- **THEN** the system SHALL generate the final Skill package using the same template-based generator used by non-interactive create

### Requirement: Interactive draft behavior is covered by automated tests
The system SHALL include automated tests for draft persistence and resume behavior.

#### Scenario: Tests cover draft workflow
- **WHEN** the test suite runs
- **THEN** it SHALL verify draft serialization, draft loading, step progression, resume behavior, missing draft failure, and final generation through the existing generator

