# intelligent-generation-fallback Specification

## Purpose
TBD - created by archiving change add-intelligent-fallback. Update Purpose after archive.
## Requirements
### Requirement: Create automatically selects LLM when available
The system SHALL automatically decide whether non-interactive Skill generation should use LLM field generation when the user does not explicitly enable or disable LLM usage.

#### Scenario: Default create without LLM configuration uses deterministic generation
- **WHEN** a user runs `skill-forge create "<requirement>"` without `--llm` or `--no-llm`
- **AND** required LLM configuration is missing
- **THEN** the system SHALL generate the Skill package through the deterministic path
- **AND** the command SHALL NOT fail because LLM configuration is missing

#### Scenario: Default create with available LLM uses LLM generation
- **WHEN** a user runs `skill-forge create "<requirement>"` without `--llm` or `--no-llm`
- **AND** required LLM configuration is present and the provider is available according to the configured availability check
- **THEN** the system SHALL use LLM field generation before rendering the Skill package

#### Scenario: Default create falls back when LLM availability check fails
- **WHEN** a user runs `skill-forge create "<requirement>"` without `--llm` or `--no-llm`
- **AND** required LLM configuration is present but the availability check fails
- **THEN** the system SHALL generate the Skill package through the deterministic path
- **AND** the command SHALL complete without an LLM configuration error

### Requirement: Explicit LLM mode controls automatic selection
The system SHALL let users force-enable or force-disable LLM generation for non-interactive `create`.

#### Scenario: Explicit LLM mode fails when configuration is missing
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **AND** required LLM configuration is missing
- **THEN** the command SHALL exit non-zero with a clear LLM configuration error

#### Scenario: Explicit LLM mode fails when availability check fails
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **AND** required LLM configuration is present but the provider is unavailable according to the configured availability check
- **THEN** the command SHALL exit non-zero with a clear LLM availability error

#### Scenario: Explicit no-LLM mode bypasses detection
- **WHEN** a user runs `skill-forge create "<requirement>" --no-llm`
- **THEN** the system SHALL use deterministic generation
- **AND** the system SHALL NOT perform an LLM availability check

#### Scenario: Conflicting LLM flags fail clearly
- **WHEN** a user runs `skill-forge create "<requirement>" --llm --no-llm`
- **THEN** the command SHALL exit non-zero with a clear conflicting options message

### Requirement: LLM availability checks are bounded
The system SHALL keep automatic LLM availability detection fast and skippable for unconfigured users.

#### Scenario: Missing configuration skips probe
- **WHEN** required LLM configuration is missing
- **THEN** the system SHALL decide that LLM is unavailable without attempting a network probe

#### Scenario: Probe timeout is bounded
- **WHEN** the system performs an LLM availability probe
- **THEN** the probe SHALL use a timeout shorter than two seconds

### Requirement: Automatic selection is recorded in provenance
The system SHALL record enough provenance metadata to explain how LLM usage was selected for generated non-interactive packages.

#### Scenario: Provenance records auto-selected LLM
- **WHEN** default `create` automatically uses LLM generation
- **THEN** `skill-forge.json` SHALL record that LLM mode was automatic and LLM generation was used

#### Scenario: Provenance records automatic deterministic fallback
- **WHEN** default `create` falls back to deterministic generation because LLM is unavailable
- **THEN** `skill-forge.json` SHALL record that LLM mode was automatic and include the selection fallback reason

#### Scenario: Provenance records explicit no-LLM
- **WHEN** `create --no-llm` generates a package
- **THEN** `skill-forge.json` SHALL record that LLM was explicitly disabled

