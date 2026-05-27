## Why

Generated Skills are more useful when they reflect the conventions and constraints of the project where they will be used. This change adds project context scanning so Skill Forge can detect local agent rules, OpenSpec usage, README guidance, and related project files, then inject concise constraints into generated Skills.

## What Changes

- Add `skill-forge create "<requirement>" --project <path>`.
- Scan project rule and documentation files such as `AGENTS.md`, `CLAUDE.md`, `README.md`, `.opencode/`, `.claude/`, `.agents/`, `openspec/`, `config.yaml`, and `project.md`.
- Skip binary files, generated/build directories, and files above a configured size limit.
- Produce a simple project context summary with detected agent tools and detected rules.
- Convert project context into Skill constraints and inject them into generated `SKILL.md`.
- Support project context in both non-interactive and interactive create flows.
- Persist project path and context summary in interactive draft state.
- Add focused tests for project scanning, skip behavior, context summarization, constraint injection, and CLI create integration.

## Capabilities

### New Capabilities

- `project-context-generation`: Covers project context scanning, safe file selection, rule detection, summary generation, and conversion of project context into Skill constraints.

### Modified Capabilities

- `local-skill-generation`: The `create` command accepts a `--project <path>` option and generated Skill packages include project-derived constraints when project context is provided.

## Impact

- Affected command surface: adds `--project` to `skill-forge create`.
- Affected source areas: new project context reader/summarizer components, `SkillRequirement` enrichment path, CLI create wiring, interactive draft wiring, and generator inputs.
- Affected filesystem reads: reads selected text files under a user-provided project path with size/type/build-output safeguards.
- Affected output: generated `SKILL.md` constraints may include project-specific rules.
- Out of scope: LLM summarization, reading the entire source tree, changing project files, automatic install behavior, and deep code analysis.
