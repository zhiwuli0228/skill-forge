## Why

Skill Forge validation currently checks package structure and recommended sections, but it does not assess whether a Skill is well authored for reliable agent triggering and execution. The next evolution requires deterministic authoring lint rules so generated and manually edited Skills can be scored for clarity, boundaries, and platform-compatible metadata.

## What Changes

- Add warning-only authoring lint rules to `SkillValidator`.
- Check frontmatter `name` slug format and package-name consistency.
- Check `description` length and whether it includes both trigger and exclusion guidance.
- Check that core sections have meaningful content rather than only headings.
- Check workflow and quality gate density using deterministic thresholds.
- Preserve existing validation error semantics: lint findings do not make a package invalid.
- Let existing generation quality reports reflect lint warnings through the current scoring path.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `skill-validation`: Validator reports deterministic authoring lint warnings in addition to existing structural validation issues.
- `generation-quality-report`: Generated package quality reports include authoring lint warnings and score impact through the existing warning penalty model.

## Impact

- Affected modules:
  - `src/skill_forge/validator/skill_validator.py`
  - `src/skill_forge/models/quality.py`
  - `src/skill_forge/cli.py`
- Affected tests:
  - `tests/test_skill_validator.py`
  - `tests/test_generation_quality_report.py`
  - `tests/test_cli.py`
- No new third-party dependencies are expected.
