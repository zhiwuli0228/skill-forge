## Why

Generated Skills currently contain only `SKILL.md`, even when a task type benefits from a checklist or reusable reference material. Allowing blueprints to declare extra package files is the next step toward richer, more practical Skill packages while keeping generation deterministic.

## What Changes

- Extend `SkillBlueprint` with optional generated file declarations.
- Allow blueprints to declare references, assets, or scripts as relative paths with literal content.
- Generate declared files alongside `SKILL.md` when a blueprint is applied.
- Add path safety checks so generated file paths cannot escape the Skill package directory.
- Populate at least one built-in blueprint with a reference file.
- Keep Skills without file declarations as single-file packages.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `skill-blueprints`: blueprints can declare additional generated package files.
- `local-skill-generation`: generated Skill packages can include blueprint-declared references/assets/scripts.
- `skill-validation`: validation recognizes unsafe generated package file paths as invalid.

## Impact

- Updates blueprint data model and built-in YAML validation.
- Updates generator output behavior and generated package metadata.
- Adds tests for file generation, path safety, no-attachment fallback, and validation.
- Does not add quality scoring, LLM behavior, user-defined blueprint directories, or dynamic file templating.
