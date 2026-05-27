## 1. Validator Lint Rules

- [x] 1.1 Add stable warning codes for authoring lint rules.
- [x] 1.2 Implement frontmatter name slug and package-name consistency lint.
- [x] 1.3 Implement description strength lint for length, trigger guidance, and exclusion guidance.
- [x] 1.4 Implement section body lint for empty recommended sections.
- [x] 1.5 Implement workflow and quality gate density lint.

## 2. Quality Report Integration

- [x] 2.1 Ensure authoring lint warnings flow through existing validation and create quality reports.
- [x] 2.2 Preserve valid package status when only lint warnings are present.

## 3. Tests

- [x] 3.1 Add validator tests for each new authoring lint warning.
- [x] 3.2 Add quality report or create tests showing lint warnings reduce score without failing generation.
- [x] 3.3 Update existing tests where expected scores or no-difference assumptions are intentionally affected.
- [x] 3.4 Run focused tests and full `uv run pytest`.

## 4. OpenSpec Verification

- [x] 4.1 Run `openspec validate "add-skill-authoring-lint-rules" --strict`.
- [x] 4.2 Run `openspec validate --all --strict`.
