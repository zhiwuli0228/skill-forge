## 1. Eval Models and Loading

- [x] 1.1 Add eval case, assertion, result, and report models.
- [x] 1.2 Implement YAML eval case loading and validation.
- [x] 1.3 Implement deterministic directory discovery for `.yaml` and `.yml` cases.

## 2. Eval Execution

- [x] 2.1 Implement static assertion checks for required sections.
- [x] 2.2 Implement static assertion checks for required constraints.
- [x] 2.3 Implement static assertion checks for forbidden phrases.
- [x] 2.4 Persist latest `eval-report.json` in the evaluated Skill package.

## 3. CLI and Library Integration

- [x] 3.1 Add `skill-forge eval <skill-name> --case <file>`.
- [x] 3.2 Add `skill-forge eval <skill-name> --cases <dir>`.
- [x] 3.3 Display eval pass/fail details and summary.
- [x] 3.4 Update `skill-forge show` to display latest eval summary when present.

## 4. Tests

- [x] 4.1 Add eval loader tests for valid and invalid cases.
- [x] 4.2 Add evaluator tests for pass, failure, and persisted report behavior.
- [x] 4.3 Add CLI tests for single-case, batch, failure, and missing Skill behavior.
- [x] 4.4 Add library/show tests for eval summary display.
- [x] 4.5 Run focused tests and full `uv run pytest`.

## 5. OpenSpec Verification

- [x] 5.1 Run `openspec validate "add-skill-eval-cases" --strict`.
- [x] 5.2 Run `openspec validate --all --strict`.
