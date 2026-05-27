## 1. Built-in Blueprints

- [x] 1.1 Add `code-review` built-in blueprint YAML.
- [x] 1.2 Add `test-generation` built-in blueprint YAML.
- [x] 1.3 Add `openspec-change` built-in blueprint YAML.
- [x] 1.4 Ensure all built-in blueprints load, validate, and list deterministically.

## 2. Task Recognition

- [x] 2.1 Extend `RequirementAnalyzer` to recognize code review requests.
- [x] 2.2 Extend `RequirementAnalyzer` to recognize test generation requests.
- [x] 2.3 Extend `RequirementAnalyzer` to recognize OpenSpec change requests.
- [x] 2.4 Preserve generic fallback behavior for unmatched requests.

## 3. Tests and Verification

- [x] 3.1 Add tests for blueprint loader/list/show coverage of the expanded blueprint set.
- [x] 3.2 Add analyzer tests for code review, test generation, and OpenSpec change task types.
- [x] 3.3 Add create-flow tests proving each new task type uses blueprint-specific generated content.
- [x] 3.4 Run `uv run pytest` and `openspec validate add-built-in-blueprints --strict`.
