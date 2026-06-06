## MODIFIED Requirements

### Requirement: Create command generates a local Skill package
The system SHALL provide a `create` command that generates a local Skill package from a requirement string, either directly in non-interactive mode, after draft confirmation in interactive mode, or with project context when a project path is provided. The command SHALL automatically use LLM-assisted requirement field generation for non-interactive generation when LLM configuration is present and available, SHALL support explicit LLM-assisted generation with `--llm`, and SHALL support explicit deterministic generation with `--no-llm`. When a parsed requirement has a task type matching a built-in Skill blueprint, the system SHALL apply matching blueprint defaults before rendering while preserving user-derived requirement fields. When the user specifies a built-in blueprint with `--blueprint`, the system SHALL apply that blueprint before rendering and SHALL prefer it over automatic task-type matching. For LLM-assisted non-interactive generation, the system SHALL apply blueprint defaults before LLM field generation so the LLM can use those defaults as context and fallback content. After non-interactive generation, the system SHALL validate the generated package and display a quality report.

#### Scenario: Requirement string creates SKILL.md
- **WHEN** a user runs `skill-forge create "Java 存量代码 bug 定位 skill"`
- **THEN** the system SHALL create a Skill package containing `SKILL.md` under the configured output directory

#### Scenario: Generated package path is reported
- **WHEN** `skill-forge create "<requirement>"` completes successfully
- **THEN** the system SHALL display the generated Skill package path

#### Scenario: Non-interactive create reports quality
- **WHEN** `skill-forge create "<requirement>"` completes non-interactive generation
- **THEN** the system SHALL display the generated package path and quality report

#### Scenario: Non-interactive create fails on generated validation errors
- **WHEN** post-generation validation reports one or more errors
- **THEN** `skill-forge create "<requirement>"` SHALL exit non-zero with a clear invalid generated package message

#### Scenario: Non-interactive create succeeds with generated validation warnings
- **WHEN** post-generation validation reports warnings and no errors
- **THEN** `skill-forge create "<requirement>"` SHALL exit successfully and display the warnings in the quality report

#### Scenario: Default create auto-selects LLM after blueprint enrichment
- **WHEN** a user runs `skill-forge create "<requirement>"`
- **AND** LLM configuration is present and available
- **THEN** the system SHALL analyze the requirement and apply matching or explicit blueprint defaults before calling the configured LLM provider
- **AND** the system SHALL use valid LLM-returned fields before rendering

#### Scenario: Default create falls back to deterministic generation without LLM
- **WHEN** a user runs `skill-forge create "<requirement>"`
- **AND** LLM configuration is missing or unavailable
- **THEN** the system SHALL generate the Skill package through the deterministic path without requiring LLM configuration

#### Scenario: Explicit LLM-assisted create generates fields after blueprint enrichment
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **THEN** the system SHALL analyze the requirement and apply matching or explicit blueprint defaults before calling the configured LLM provider
- **AND** the system SHALL use valid LLM-returned fields before rendering

#### Scenario: Explicit no-LLM create uses deterministic generation
- **WHEN** a user runs `skill-forge create "<requirement>" --no-llm`
- **THEN** the system SHALL generate the Skill package without LLM configuration, availability checks, or LLM field generation

#### Scenario: LLM-assisted create with project context generates fields after project context enrichment
- **WHEN** a user runs `skill-forge create "<requirement>" --llm --project <path>`
- **THEN** the system SHALL apply project context constraints before calling the configured LLM provider
- **AND** the LLM-generated Skill requirement SHALL preserve the project context constraints unless a supported field is validly replaced

#### Scenario: Auto-selected LLM create with project context generates fields after project context enrichment
- **WHEN** a user runs `skill-forge create "<requirement>" --project <path>`
- **AND** LLM configuration is present and available
- **THEN** the system SHALL apply project context constraints before calling the configured LLM provider
- **AND** the LLM-generated Skill requirement SHALL preserve the project context constraints unless a supported field is validly replaced

#### Scenario: Interactive create enters draft workflow
- **WHEN** a user runs `skill-forge create "<requirement>" --interactive`
- **THEN** the system SHALL enter the interactive draft workflow before generating the Skill package

#### Scenario: Project context create injects constraints
- **WHEN** a user runs `skill-forge create "<requirement>" --project <path>`
- **THEN** the system SHALL read supported project context from `<path>` and include derived project constraints in the generated Skill package

#### Scenario: Use matching blueprint defaults
- **WHEN** the analyzed requirement has a task type matching a built-in Skill blueprint
- **THEN** the system SHALL apply the blueprint defaults before rendering the Skill package
- **AND** the generated `SKILL.md` includes blueprint-provided workflow, constraints, outputs, or quality gates that were missing from the analyzed requirement

#### Scenario: Fall back without matching blueprint
- **WHEN** the analyzed requirement does not have a matching built-in Skill blueprint
- **THEN** the system SHALL generate the Skill package through the existing generic requirement fields

#### Scenario: Preserve user-derived requirement fields
- **WHEN** the analyzer extracts constraints or expected outputs from the user's requirement
- **THEN** blueprint enrichment SHALL preserve those user-derived values in the generated Skill

#### Scenario: Explicit blueprint selection
- **WHEN** a user runs `skill-forge create "Python 服务 review" --blueprint code-review`
- **THEN** the system SHALL apply the `code-review` blueprint before rendering the Skill package

#### Scenario: Explicit blueprint overrides automatic matching
- **WHEN** a user runs `skill-forge create "Python 代码审查 skill" --blueprint test-generation`
- **THEN** the system SHALL apply the `test-generation` blueprint instead of the automatically matched `code-review` blueprint

#### Scenario: Missing explicit blueprint fails clearly
- **WHEN** a user runs `skill-forge create "Python 服务 review" --blueprint missing-blueprint`
- **THEN** the system SHALL exit non-zero with a clear missing blueprint message
