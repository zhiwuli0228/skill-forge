## 1. Recommendation Models and Service

- [x] 1.1 Define recommendation and comparison models under `src/skill_forge/lifecycle/`.
- [x] 1.2 Implement a deterministic recommendation service that consumes lifecycle summaries.
- [x] 1.3 Map lifecycle states to conservative next-best-action labels and reasons.
- [x] 1.4 Implement deterministic compare logic with stable tie-breakers and explainable output.

## 2. CLI Integration

- [x] 2.1 Add `skill-forge lifecycle recommend <skill-name>` to the CLI.
- [x] 2.2 Add `skill-forge lifecycle compare <skill-a> <skill-b>` to the CLI.
- [x] 2.3 Render recommendation and comparison output without mutating files.

## 3. Tests and Validation

- [x] 3.1 Add focused tests for recommendation output across healthy, regressed, missing-fact, and unknown lifecycle states.
- [x] 3.2 Add focused tests for compare output and deterministic tie-breaking.
- [x] 3.3 Add CLI tests for recommend and compare commands, including missing-skill failure paths.
- [x] 3.4 Run focused tests for lifecycle and CLI behavior.
- [x] 3.5 Run the full test suite.
- [x] 3.6 Run `openspec validate \"add-skill-lifecycle-recommendation\" --strict`.
- [x] 3.7 Update the lifecycle governance plan with implementation progress and next-step status.
