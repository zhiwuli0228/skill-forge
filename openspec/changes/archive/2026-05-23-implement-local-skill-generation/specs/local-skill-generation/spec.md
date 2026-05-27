## ADDED Requirements

### Requirement: Create command generates a local Skill package
The system SHALL provide a non-interactive `create` command that generates a local Skill package from a requirement string.

#### Scenario: Requirement string creates SKILL.md
- **WHEN** a user runs `skill-forge create "Java 存量代码 bug 定位 skill"`
- **THEN** the system SHALL create a Skill package containing `SKILL.md` under the configured output directory

#### Scenario: Generated package path is reported
- **WHEN** `skill-forge create "<requirement>"` completes successfully
- **THEN** the system SHALL display the generated Skill package path

### Requirement: Requirement analyzer derives structured generation input
The system SHALL transform a natural language requirement into a structured Skill requirement without requiring network access or an LLM.

#### Scenario: Java bug investigation requirement is parsed
- **WHEN** the analyzer receives `我需要一个用于 Java 存量代码 bug 定位的 skill，要求先分析日志，再读代码，不能直接修改代码，要输出根因、修复方案和测试建议。`
- **THEN** it SHALL produce a requirement with name `java-bug-investigation`, software engineering domain, bug investigation task type, constraints about analyzing logs before code changes, and expected outputs for root cause, fix plan, and test plan

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
