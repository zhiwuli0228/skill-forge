## Why

Skill Forge now has validatable built-in Skill blueprints, but `create` still ignores them and relies on hardcoded defaults. Connecting blueprints to generation is the next small step toward fast, task-specific Skill creation while preserving the existing fallback path.

## What Changes

- Add blueprint matching by `SkillRequirement.task_type`.
- Add a merge step that applies matching blueprint defaults to a parsed `SkillRequirement`.
- Preserve user-derived requirement fields when they are already populated.
- Keep project context constraint injection after blueprint defaults are applied.
- Keep unknown or unmatched requirements on the existing generic generation path.
- Do not add a `--blueprint` option, reference generation, quality scoring, or additional built-in blueprints in this change.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `local-skill-generation`: `create` can use a matching built-in blueprint to fill missing Skill requirement fields before rendering.
- `skill-blueprints`: built-in blueprints can be selected programmatically by task type for generation.

## Impact

- Adds a blueprint-backed requirement enrichment service.
- Updates `skill-forge create` to enrich analyzed requirements before generation.
- Updates tests for generated Java bug Skills and generic fallback behavior.
- Does not change command syntax or add dependencies.
