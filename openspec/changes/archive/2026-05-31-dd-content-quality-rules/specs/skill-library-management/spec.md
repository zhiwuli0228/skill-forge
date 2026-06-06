## MODIFIED Requirements

### Requirement: Library inspection exposes generation provenance
The system SHALL expose generation provenance metadata for generated Skill packages when `skill-forge.json` exists, including persisted content quality metrics when they are present.

#### Scenario: Show generated Skill with provenance
- **WHEN** a user runs `skill-forge show <skill-name>` for a package containing `skill-forge.json`
- **THEN** the command SHALL display provenance fields including blueprint, LLM usage, quality, content quality metrics when present, and generated timestamp

#### Scenario: Show generated Skill without provenance
- **WHEN** a user runs `skill-forge show <skill-name>` for a package without `skill-forge.json`
- **THEN** the command SHALL still display existing package metadata and SHALL indicate missing provenance without failing

#### Scenario: Show generated Skill with content quality metrics
- **WHEN** a user runs `skill-forge show <skill-name>` for a package whose provenance contains content quality metrics
- **THEN** the command SHALL display workflow specificity, constraint verifiability, and quality gate clarity values from provenance
