## ADDED Requirements

### Requirement: Generated packages include provenance metadata
The system SHALL write a `skill-forge.json` provenance metadata file into each newly generated non-interactive Skill package.

#### Scenario: Create writes provenance metadata
- **WHEN** `skill-forge create "<requirement>"` completes successfully
- **THEN** the generated package SHALL include `skill-forge.json`

#### Scenario: Metadata records generation inputs
- **WHEN** `skill-forge create "<requirement>"` writes provenance metadata
- **THEN** the metadata SHALL include schema version, generation timestamp, skill name, original requirement text, target platform, language, task type, LLM usage, and project context path when supplied

#### Scenario: Metadata records applied blueprint
- **WHEN** generation applies an automatic or explicit blueprint
- **THEN** the metadata SHALL include the applied blueprint ID and source when known

#### Scenario: Metadata records quality and attachments
- **WHEN** post-generation validation and quality reporting complete
- **THEN** the metadata SHALL include quality score, quality status, and generated references, assets, and scripts manifests

#### Scenario: Metadata avoids full project context
- **WHEN** generation uses `--project <path>`
- **THEN** the metadata SHALL store the project path but SHALL NOT store the full project context text
