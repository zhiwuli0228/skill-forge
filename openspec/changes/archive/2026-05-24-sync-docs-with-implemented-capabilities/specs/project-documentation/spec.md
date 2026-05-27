## ADDED Requirements

### Requirement: Documentation reflects implemented CLI capabilities
Project documentation SHALL describe implemented Skill Forge CLI commands and options consistently with the executable CLI surface.

#### Scenario: README lists implemented generation options
- **WHEN** a user reads the README command documentation
- **THEN** the documentation SHALL describe `create --blueprint`, `create --llm`, and post-generation quality reporting as available capabilities

#### Scenario: README lists generated Skill library commands
- **WHEN** a user reads the README command documentation
- **THEN** the documentation SHALL describe `list`, `show`, and `diff` as available generated Skill library commands

#### Scenario: README lists blueprint inspection commands
- **WHEN** a user reads the README command documentation
- **THEN** the documentation SHALL describe `blueprints list` and `blueprints show <blueprint-id>` as available commands

### Requirement: Documentation separates completed capabilities from future work
Project documentation SHALL distinguish completed capabilities from future enhancement candidates.

#### Scenario: Completed roadmap remains visible
- **WHEN** a contributor reads the skill generation roadmap
- **THEN** the documentation SHALL preserve the archived completed roadmap entries and their verification context

#### Scenario: Future work is listed separately
- **WHEN** a contributor reads the skill generation roadmap
- **THEN** the documentation SHALL list next-stage enhancement candidates separately from completed capabilities

#### Scenario: Current scope omits stale missing-capability claims
- **WHEN** a user reads the README current scope section
- **THEN** the documentation SHALL NOT list LLM-assisted generation or generated Skill library `list`/`show`/`diff` commands as unimplemented

### Requirement: Archived main specs have stable purposes
Main OpenSpec specs for implemented capabilities SHALL include stable purpose text instead of archive placeholder text.

#### Scenario: LLM assisted generation spec has a purpose
- **WHEN** a contributor reads `openspec/specs/llm-assisted-generation/spec.md`
- **THEN** the spec SHALL describe the purpose of optional LLM-assisted Skill requirement refinement

#### Scenario: Skill library management spec has a purpose
- **WHEN** a contributor reads `openspec/specs/skill-library-management/spec.md`
- **THEN** the spec SHALL describe the purpose of generated Skill library listing, inspection, and diffing

### Requirement: Documentation cleanup avoids runtime behavior changes
The documentation synchronization change SHALL NOT alter Skill Forge runtime behavior.

#### Scenario: Existing tests still pass
- **WHEN** the documentation synchronization is implemented
- **THEN** the existing automated test suite SHALL continue to pass without requiring CLI behavior changes

#### Scenario: OpenSpec artifacts validate
- **WHEN** the documentation synchronization change is ready for implementation review
- **THEN** `openspec validate "sync-docs-with-implemented-capabilities" --strict` SHALL pass
