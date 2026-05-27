## Why

Generated Skill packages currently contain `SKILL.md` and optional attachments, but they do not record how they were produced. Without generation provenance, users cannot reliably inspect the source requirement, blueprint choice, LLM usage, project context, validation outcome, or attachment manifest needed for later evaluation and upgrade workflows.

## What Changes

- Write a `skill-forge.json` metadata file into each newly generated Skill package.
- Record stable schema version, generation timestamp, original requirement text, target platform, language, selected blueprint information, LLM usage, project context path, quality summary, and attachment manifests.
- Extend generated Skill library inspection to read and display provenance metadata when present.
- Preserve backward compatibility for existing generated Skill packages without metadata.
- Extend `diff` to report metadata differences in addition to `SKILL.md` content differences.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `local-skill-generation`: Generated packages include `skill-forge.json` provenance metadata.
- `skill-library-management`: Library `show` and `diff` commands expose provenance metadata when it exists while supporting old packages without metadata.

## Impact

- Affected modules:
  - `src/skill_forge/models/generated.py`
  - `src/skill_forge/generator/skill_generator.py`
  - `src/skill_forge/library/manager.py`
  - `src/skill_forge/cli.py`
- Affected tests:
  - `tests/test_skill_generator.py`
  - `tests/test_skill_library.py`
  - `tests/test_cli.py`
- No new third-party dependencies are expected.
