## ADDED Requirements

### Requirement: LLM assistance supports automatic and explicit modes
The system SHALL support LLM-assisted field generation through automatic selection by default, explicit force-enable mode, and explicit force-disable mode.

#### Scenario: Default create uses LLM when available
- **WHEN** a user runs `skill-forge create "<requirement>"`
- **AND** LLM configuration and availability checks pass
- **THEN** the system SHALL analyze the requirement and apply applicable blueprint defaults before sending structured requirement context to the configured LLM provider
- **AND** the system SHALL use valid returned structured fields when generating the Skill package

#### Scenario: Default create falls back without LLM
- **WHEN** a user runs `skill-forge create "<requirement>"`
- **AND** LLM configuration or availability checks do not pass
- **THEN** the system SHALL use deterministic generation without requiring the user to pass `--no-llm`

#### Scenario: Explicit LLM requests field generation
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **THEN** the system SHALL analyze the requirement and apply applicable blueprint defaults before sending structured requirement context to the configured LLM provider
- **AND** the system SHALL use valid returned structured fields when generating the Skill package

#### Scenario: Explicit no-LLM disables field generation
- **WHEN** a user runs `skill-forge create "<requirement>" --no-llm`
- **THEN** the system SHALL use the deterministic generation path without LLM configuration or network access

## REMOVED Requirements

### Requirement: LLM assistance is opt-in
**Reason**: LLM field generation has been validated as useful and the roadmap now requires automatic selection when a provider is configured.
**Migration**: Use `--no-llm` for guaranteed deterministic generation; use `--llm` to force LLM generation and receive errors when the provider is unavailable.
