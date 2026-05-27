## Why

Skill Forge now reports structural validation issues and authoring lint warnings, but users still have to infer what to change. Deterministic repair suggestions close the next quality loop by mapping known issue codes to actionable guidance without modifying files or invoking an LLM.

## What Changes

- Add structured repair suggestions derived from validation issue codes.
- Include suggestions in generation quality reports.
- Display suggestions after `skill-forge validate` and non-interactive `skill-forge create` when issues exist.
- Keep suggestions deterministic and stable for tests and future automation.
- Do not automatically modify Skill files.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `skill-validation`: Validation output can include deterministic repair suggestions for known errors and warnings.
- `generation-quality-report`: Quality reports include deterministic repair suggestions alongside validation issues and next actions.

## Impact

- Affected modules:
  - `src/skill_forge/models/quality.py`
  - `src/skill_forge/cli.py`
  - `src/skill_forge/validator/skill_validator.py`
- Affected tests:
  - `tests/test_generation_quality_report.py`
  - `tests/test_cli.py`
  - `tests/test_skill_validator.py`
- No new third-party dependencies are expected.
