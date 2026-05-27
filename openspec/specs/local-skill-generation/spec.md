# local-skill-generation Specification

## Purpose
Define how Skill Forge turns natural-language requirements into local Skill packages through deterministic requirement analysis, optional blueprint enrichment, project context constraints, and template rendering.
## Requirements
### Requirement: Create command generates a local Skill package
The system SHALL provide a `create` command that generates a local Skill package from a requirement string, either directly in non-interactive mode, after draft confirmation in interactive mode, or with project context when a project path is provided. The command SHALL support optional LLM-assisted requirement refinement only when `--llm` is supplied. When a parsed or refined requirement has a task type matching a built-in Skill blueprint, the system SHALL apply matching blueprint defaults before rendering while preserving user-derived requirement fields. When the user specifies a built-in blueprint with `--blueprint`, the system SHALL apply that blueprint before rendering and SHALL prefer it over automatic task-type matching. After non-interactive generation, the system SHALL validate the generated package and display a quality report.

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

#### Scenario: LLM-assisted create refines requirement
- **WHEN** a user runs `skill-forge create "<requirement>" --llm`
- **THEN** the system SHALL refine the analyzed requirement through the configured LLM provider before rendering

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

### Requirement: Requirement analyzer derives structured generation input
The system SHALL transform a natural language requirement into a structured Skill requirement without requiring network access or an LLM. The analyzer SHALL identify obvious requests for bug investigation, code review, test generation, and OpenSpec change workflows so blueprint-backed generation can use the matching built-in defaults.

#### Scenario: Java bug investigation requirement is parsed
- **WHEN** the analyzer receives `我需要一个用于 Java 存量代码 bug 定位的 skill，要求先分析日志，再读代码，不能直接修改代码，要输出根因、修复方案和测试建议。`
- **THEN** it SHALL produce a requirement with name `java-bug-investigation`, software engineering domain, bug investigation task type, constraints about analyzing logs before code changes, and expected outputs for root cause, fix plan, and test plan

#### Scenario: Code review requirement is parsed
- **WHEN** the analyzer receives `Python 代码审查 skill`
- **THEN** it SHALL produce a requirement with code review task type suitable for blueprint-backed generation

#### Scenario: Test generation requirement is parsed
- **WHEN** the analyzer receives `为这个项目生成测试编写 skill`
- **THEN** it SHALL produce a requirement with test generation task type suitable for blueprint-backed generation

#### Scenario: OpenSpec change requirement is parsed
- **WHEN** the analyzer receives `OpenSpec change 分析 skill`
- **THEN** it SHALL produce a requirement with OpenSpec change task type suitable for blueprint-backed generation

#### Scenario: Vague requirement still produces usable defaults
- **WHEN** the analyzer receives a requirement that does not match a specific task rule
- **THEN** it SHALL still produce a valid skill name, description, usage boundaries, workflow, output format, and quality gates suitable for template rendering

### Requirement: Generated SKILL.md uses the standard template structure
The system SHALL render generated `SKILL.md` content from a template with stable frontmatter and standard sections.

#### Scenario: Frontmatter is included
- **WHEN** a Skill package is generated
- **THEN** `SKILL.md` SHALL include frontmatter with non-empty `name` and `description`

#### Scenario: Standard sections are included
- **WHEN** a Skill package is generated
- **THEN** `SKILL.md` SHALL include Purpose, When to use, When not to use, Required inputs, Workflow, Constraints, Output format, and Quality gates sections

### Requirement: Generated output respects configured output directory
The system SHALL write generated Skill packages under the configured output directory.

#### Scenario: Default output directory is used
- **WHEN** no user config overrides the create output directory
- **THEN** generated packages SHALL be written under `~/.skill-forge/output/<skill-name>/`

#### Scenario: Existing package is not silently overwritten
- **WHEN** a generated package directory already exists for the same skill name
- **THEN** the system SHALL fail with a clear message instead of silently overwriting existing files

### Requirement: Local generation is covered by automated tests
The system SHALL include focused automated tests for local Skill generation behavior.

#### Scenario: Tests verify generation workflow
- **WHEN** the test suite runs
- **THEN** it SHALL verify requirement analysis, template rendering, output directory behavior, non-overwrite behavior, and CLI create integration using isolated test paths

### Requirement: Blueprint-declared files are generated
The system SHALL write blueprint-declared references, assets, and scripts into generated Skill packages when the applied blueprint declares them.

#### Scenario: Generate blueprint-declared reference
- **WHEN** a user creates a Skill using a blueprint that declares `references/diagnosis-checklist.md`
- **THEN** the generated Skill package SHALL include `references/diagnosis-checklist.md` with the declared content

#### Scenario: Generate single-file package without declarations
- **WHEN** a user creates a Skill using a blueprint that declares no references, assets, or scripts
- **THEN** the generated Skill package SHALL contain `SKILL.md` and no generated attachment files

#### Scenario: Generated package metadata includes attachments
- **WHEN** the generator writes blueprint-declared files
- **THEN** the returned package metadata SHALL include the generated attachment paths grouped by references, assets, or scripts

### Requirement: Generated attachment paths remain inside package
The system SHALL prevent blueprint-declared files from being written outside the generated Skill package directory.

#### Scenario: Reject path traversal during generation
- **WHEN** generation receives a declared file path that resolves outside the package directory
- **THEN** generation SHALL fail before writing that file outside the package

### Requirement: Generated packages are discoverable
Generated Skill packages SHALL be discoverable by local Skill library management commands after creation.

#### Scenario: Created package appears in library
- **WHEN** `skill-forge create "<requirement>"` successfully generates a Skill package
- **THEN** `skill-forge list` SHALL be able to display that generated package from the configured output directory

### Requirement: Create can use custom blueprints
The system SHALL allow explicit blueprint selection during Skill generation to use built-in, user-level, or project-level blueprints that are in scope for the command.

#### Scenario: Create with user custom blueprint
- **WHEN** a user runs `skill-forge create "<requirement>" --blueprint <custom-id>` and `<custom-id>` exists in the user blueprint root
- **THEN** the system SHALL apply that custom blueprint before rendering the Skill package

#### Scenario: Create with project custom blueprint
- **WHEN** a user runs `skill-forge create "<requirement>" --project <path> --blueprint <custom-id>` and `<custom-id>` exists in `<path>/.skill-forge/blueprints`
- **THEN** the system SHALL apply that project custom blueprint before rendering the Skill package

#### Scenario: Create without custom blueprints preserves built-in behavior
- **WHEN** a user runs `skill-forge create "<requirement>"` without custom blueprint roots containing matching blueprints
- **THEN** the system SHALL preserve the existing built-in blueprint matching and fallback behavior

#### Scenario: Duplicate custom blueprint IDs fail generation clearly
- **WHEN** `skill-forge create "<requirement>" --blueprint <id>` loads multiple in-scope blueprints with ID `<id>`
- **THEN** the system SHALL exit non-zero with a clear duplicate blueprint ID message

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

