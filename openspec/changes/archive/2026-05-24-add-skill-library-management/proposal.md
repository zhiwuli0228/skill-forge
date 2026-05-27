## Why

Skill Forge can now generate higher-quality Skill packages, but users still have to inspect the output directory manually to find, review, or compare generated Skills. A small local library surface makes generated packages manageable without changing generation quality logic or install behavior.

## What Changes

- Add commands to inspect generated Skill packages under the configured output directory:
  - `skill-forge list`
  - `skill-forge show <skill-name>`
  - `skill-forge diff <skill-a> <skill-b>`
- Read metadata from each package `SKILL.md` frontmatter and package files.
- Show clear errors when generated Skills are missing or invalid enough to inspect.
- Keep all behavior local; no remote marketplace, automatic upgrade, or generation logic changes.

## Capabilities

### New Capabilities

- `skill-library-management`: Covers listing generated Skills, showing package metadata, and diffing generated `SKILL.md` files.

### Modified Capabilities

- `local-skill-generation`: Generated Skill packages are discoverable as local library entries after creation.

## Impact

- Affected code: new library reader/manager module, `src/skill_forge/cli.py`, and tests.
- Affected command surface: new top-level `list`, `show`, and `diff` commands.
- No new dependencies; use standard library diffing and existing frontmatter parsing.
