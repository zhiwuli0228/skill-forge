## Why

Generated Skill packages currently require a separate `validate` command before users can see structural issues. As generation now produces richer packages with optional blueprint-declared files, `create` should immediately surface validation status, quality score, warnings, and next actions without introducing repair or LLM behavior.

## What Changes

- Run Skill validation automatically after non-interactive `create` generates a package.
- Add a deterministic quality report that includes validation status, score, errors, warnings, and suggested next actions.
- Print the quality report in the `create` success output.
- Fail `create` with a clear message if post-generation validation reports errors.
- Keep warnings non-blocking and keep `validate` as the explicit standalone validation command.

## Capabilities

### New Capabilities

- `generation-quality-report`: Covers post-generation validation summaries, deterministic quality scoring, report contents, and create-command behavior.

### Modified Capabilities

- `local-skill-generation`: `create` now reports post-generation quality details and fails clearly if generated output is invalid.
- `skill-validation`: validation results now support deterministic quality report construction without changing validator rules.

## Impact

- Affected code: `src/skill_forge/cli.py`, validation/reporting models or helpers, and focused tests.
- Affected commands: `skill-forge create` output gains a quality report; `skill-forge validate` remains compatible.
- No new dependencies, network access, automatic repair, or LLM integration.
