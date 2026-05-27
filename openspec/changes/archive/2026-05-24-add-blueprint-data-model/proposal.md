## Why

Skill Forge can currently generate Skills from a requirement string, but its generation inputs are still mostly hardcoded rules and a single common template. To support faster, higher-quality Skill generation later, the project needs a stable blueprint data layer that can describe task-specific Skill defaults before those blueprints are connected to `create`.

## What Changes

- Add a `SkillBlueprint` data model for task-specific Skill defaults.
- Define a small YAML blueprint file format that maps closely to existing `SkillRequirement` fields.
- Add a built-in blueprint directory with one initial `bug-investigation` blueprint.
- Add a blueprint loader that discovers, parses, sorts, and validates built-in blueprints.
- Add CLI inspection commands:
  - `skill-forge blueprints list`
  - `skill-forge blueprints show <blueprint-id>`
- Keep the existing `create`, `validate`, and `install` behavior unchanged.

## Capabilities

### New Capabilities

- `skill-blueprints`: Defines how Skill Forge exposes loadable, validatable, inspectable Skill blueprints.

### Modified Capabilities

- None.

## Impact

- Adds blueprint models, loading logic, and tests under `src/skill_forge/`.
- Adds a built-in blueprint configuration directory.
- Extends the Typer CLI with a `blueprints` command group.
- Does not add runtime dependencies.
- Does not change generated Skill output or installation behavior.
