## Why

Project documentation no longer matches the implemented Skill Forge CLI. The roadmap and code show blueprint-backed generation, optional LLM refinement, quality reports, and local library management are implemented, while README material still describes some of those capabilities as missing.

This change aligns the user-facing docs and archived main specs with the actual product surface so future users and contributors can trust the documented project state.

## What Changes

- Update README documentation to describe the implemented capabilities accurately.
- Remove stale "not implemented" claims for LLM-assisted generation and generated Skill library commands.
- Document the current `create --blueprint`, `create --llm`, `blueprints list/show`, `list`, `show`, and `diff` workflows.
- Replace placeholder `Purpose` text in archived main specs with stable capability descriptions.
- Add a next-stage roadmap section that distinguishes completed capabilities from future enhancements.
- No CLI behavior, public API, storage schema, or runtime dependency changes are introduced.

## Capabilities

### New Capabilities
- `project-documentation`: Project documentation SHALL accurately reflect implemented CLI capabilities, current roadmap state, and archived capability purposes.

### Modified Capabilities
- None.

## Impact

- Affected docs:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/skill_generation_roadmap.md`
  - `docs/skill_forge_design_doc.md` if command and capability references need alignment
- Affected OpenSpec files:
  - `openspec/specs/llm-assisted-generation/spec.md`
  - `openspec/specs/skill-library-management/spec.md`
  - New change spec under `openspec/changes/sync-docs-with-implemented-capabilities/specs/project-documentation/spec.md`
- No application code changes are expected.
