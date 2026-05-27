## 1. Suggestion Model and Mapping

- [x] 1.1 Add a structured `RepairSuggestion` model.
- [x] 1.2 Add deterministic issue-code-to-suggestion mapping for current validation errors.
- [x] 1.3 Add deterministic issue-code-to-suggestion mapping for current validation and authoring lint warnings.
- [x] 1.4 Add fallback suggestion handling for unknown issue codes.

## 2. Quality and CLI Integration

- [x] 2.1 Add repair suggestions to `GenerationQualityReport`.
- [x] 2.2 Display suggestions in `skill-forge validate` when validation issues exist.
- [x] 2.3 Display suggestions in non-interactive `skill-forge create` quality output when validation issues exist.
- [x] 2.4 Omit suggestions output when there are no issues.

## 3. Tests

- [x] 3.1 Add quality report tests for warning, error, and clean suggestion behavior.
- [x] 3.2 Add CLI validate tests for suggestions with errors and warnings.
- [x] 3.3 Add CLI create tests for suggestions in quality output.
- [x] 3.4 Run focused tests and full `uv run pytest`.

## 4. OpenSpec Verification

- [x] 4.1 Run `openspec validate "add-deterministic-repair-suggestions" --strict`.
- [x] 4.2 Run `openspec validate --all --strict`.
