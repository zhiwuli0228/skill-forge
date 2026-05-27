## Why

Blueprint-backed generation currently has only one useful built-in task type. To make fast Skill generation valuable across common coding-agent workflows, Skill Forge needs a small first set of high-value built-in blueprints and deterministic recognition rules that route natural-language requests to them.

## What Changes

- Add built-in blueprints for:
  - `code-review`
  - `test-generation`
  - `openspec-change`
- Keep the existing `bug-investigation` blueprint.
- Extend the rule-based `RequirementAnalyzer` to identify code review, test generation, and OpenSpec change requests.
- Ensure generated Skills for these task types include task-specific workflows, outputs, constraints, and quality gates from their blueprints.
- Add tests for blueprint listing/showing, task recognition, and generated content for each new blueprint.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `skill-blueprints`: expands the built-in blueprint set from one task type to four high-value task types.
- `local-skill-generation`: expands deterministic task recognition so `create` can route common requests to matching blueprints.

## Impact

- Adds built-in YAML blueprint files.
- Updates the rule-based requirement analyzer.
- Adds tests for new blueprint files, task recognition, and generated output.
- Does not change the blueprint schema, command syntax, package shape, or dependencies.
