## 1. Lifecycle Model and Service

- [x] 1.1 Define lifecycle summary, state, and evidence models under `src/skill_forge/lifecycle/`.
- [x] 1.2 Implement a read-only lifecycle service that reads provenance, eval, quality, and experience facts for a generated Skill.
- [x] 1.3 Classify lifecycle state deterministically with a small set of conservative labels.
- [x] 1.4 Ensure missing facts still produce a summary instead of failing.

## 2. CLI Integration

- [x] 2.1 Add `skill-forge lifecycle show <skill-name>` to the CLI.
- [x] 2.2 Render lifecycle state, evidence summaries, and missing-fact notes in the CLI output.
- [x] 2.3 Keep existing `show`, `list`, `diff`, and `upgrade` behavior unchanged.

## 3. Tests and Validation

- [x] 3.1 Add focused tests for lifecycle summaries with full facts, partial facts, and missing facts.
- [x] 3.2 Add CLI tests for lifecycle show output and read-only behavior.
- [x] 3.3 Run focused tests for lifecycle, library, CLI, and experience behavior.
- [x] 3.4 Run the full test suite.
- [x] 3.5 Run `openspec validate \"add-skill-lifecycle-index\" --strict`.
- [x] 3.6 Update the lifecycle governance plan with implementation progress and the new next-step status.
