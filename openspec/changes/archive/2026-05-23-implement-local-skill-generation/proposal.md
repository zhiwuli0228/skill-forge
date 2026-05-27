## Why

Skill Forge can initialize its local workspace, but it still cannot produce a Skill package. This change adds the first useful product workflow: generating a local, template-driven `SKILL.md` from a user requirement without network access, interaction, or LLM dependency.

## What Changes

- Add a `skill-forge create "<requirement>"` command for non-interactive local Skill generation.
- Add core generation data models for structured requirements and generated package metadata.
- Add a rule-based requirement analyzer that derives a skill name, domain, task type, constraints, expected outputs, and default usage boundaries from natural language.
- Add Jinja2 template rendering for a standard `SKILL.md`.
- Write generated Skill packages to the configured output directory, defaulting to `~/.skill-forge/output/<skill-name>/`.
- Include standard sections in generated `SKILL.md`: Purpose, When to use, When not to use, Required inputs, Workflow, Constraints, Output format, and Quality gates.
- Add focused tests for requirement parsing, template rendering, output path behavior, and the `create` command.

## Capabilities

### New Capabilities

- `local-skill-generation`: Covers non-interactive, offline Skill generation from a requirement string into a local Skill package.

### Modified Capabilities

- None.

## Impact

- Affected command surface: adds `skill-forge create "<requirement>"`.
- Affected source areas: new requirement analyzer, generation models, template renderer, Skill generator, and CLI command wiring.
- Affected local filesystem: writes generated Skill packages under the configured output directory.
- Affected dependencies: uses existing dependencies including Pydantic and Jinja2; no new runtime dependency is expected.
- Out of scope: interactive prompts, draft persistence, static validation, installation, project context reading, research corpus retrieval, network refresh, and LLM-enhanced generation.
