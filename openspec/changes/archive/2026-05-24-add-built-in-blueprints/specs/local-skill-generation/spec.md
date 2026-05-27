## MODIFIED Requirements

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
