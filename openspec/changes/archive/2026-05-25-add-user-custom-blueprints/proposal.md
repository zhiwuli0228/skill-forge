## Why

Skill Forge currently supports only repository-owned built-in blueprints. This limits the project’s next goal of quickly producing team-specific standard Skills because teams cannot maintain private blueprint standards in their user or project workspace.

## What Changes

- Add support for user-level custom blueprint directories under the Skill Forge home directory.
- Add support for project-level custom blueprint directories when `--project <path>` is provided.
- Extend blueprint listing, inspection, and generation to use built-in, user, and project blueprint roots together.
- Display blueprint source information so users can distinguish built-in, user, and project blueprints.
- Reject duplicate blueprint IDs across loaded roots with a clear error to keep generation deterministic.
- Preserve existing built-in-only behavior when no custom blueprints exist.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `skill-blueprints`: Blueprints can be loaded from built-in, user-level, and project-level roots with source metadata and duplicate-ID detection.
- `local-skill-generation`: `create --blueprint <id>` can apply a custom blueprint from the configured user root or the selected project root.

## Impact

- Affected CLI:
  - `skill-forge blueprints list`
  - `skill-forge blueprints show <blueprint-id>`
  - `skill-forge create "<requirement>" --blueprint <blueprint-id>`
- Affected modules:
  - `src/skill_forge/blueprints/loader.py`
  - `src/skill_forge/blueprints/enricher.py`
  - `src/skill_forge/models/blueprint.py`
  - `src/skill_forge/config.py`
  - `src/skill_forge/storage/paths.py`
  - `src/skill_forge/cli.py`
- Affected tests:
  - `tests/test_blueprints.py`
  - `tests/test_cli.py`
  - `tests/test_skill_generator.py`
- No new third-party dependencies are expected.
