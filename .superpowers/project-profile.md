# Superpowers Project Profile

This file is the **project profile** that Superpowers reads when it enters the Skill Forge repository. It tells Superpowers what the project is, what stack it uses, what constraints apply, and where to find the project-specific governance rules.

## 1. Project Snapshot

- **Name**: `skill-forge`
- **Type**: local-first CLI workspace
- **Purpose**: design, generate, validate, update, search, upgrade, install, and govern AI agent Skills (`SKILL.md` packages) for Codex, opencode, and Claude Code.
- **Governance model**: OpenSpec lifecycle + SuperSpec-style artifacts + Superpowers discipline + Project Harness constraints.
- **Current schema**: `skill-forge-governance` (project-local, see `openspec/schemas/skill-forge-governance/`).

## 2. Technology Stack

- **Language**: Python 3.11+
- **Package manager**: `uv`
- **CLI framework**: Typer
- **Data models**: Pydantic / pydantic-settings
- **Templates**: Jinja2
- **Terminal UI**: Rich / Questionary
- **Config format**: YAML
- **Local metadata**: SQLite
- **Retrieval**: deterministic local retrieval first
- **Test framework**: pytest

## 3. Core Constraints

These are the constraints Superpowers must respect when suggesting or executing work. They come from `openspec/config.yaml` `context:` and are restated here for Superpowers' quick reference.

- **local-first**: data and state stay on the user's machine. No required network calls in the default flow.
- **deterministic generation**: the default generation path is deterministic and reproducible. LLM refinement is opt-in.
- **generated Skill provenance**: every generated Skill package carries `skill-forge.json` recording source blueprint, requirement, schema version, and LLM selection.
- **validation-first quality**: generated Skills pass static validation before installation or upgrade. Validation results are part of the artifact.
- **platform adapter isolation**: Codex, opencode, and Claude adapter code lives in isolated modules. Platform-specific behavior does not leak into shared core modules.
- **bounded project context ingestion**: project context is read from a fixed allowlist (`AGENTS.md`, `CLAUDE.md`, `README.md`, `.opencode/`, `.claude/`, `.agents/`, `openspec/`). Bounded line counts and total size.
- **chat history independence**: generated artifacts must not silently depend on prior chat context. Every artifact must be derivable from inputs on disk and the change folder.
- **backward compatibility**: existing Skill Forge workspaces (config, drafts, output, corpus) must keep working. Schema changes are additive and versioned.

## 4. Agent Role Map

| Agent        | Primary role                                          | See                                            |
|--------------|-------------------------------------------------------|------------------------------------------------|
| Codex        | Design, planning, OpenSpec change artifacts           | `CODEX.md`                                     |
| Claude Code  | Implementation, tests, verification, evidence        | `CLAUDE.md`                                    |
| opencode     | Fallback execution under strict scope                | `OPENCODE.md`                                  |
| Superpowers  | Execution discipline (this profile)                  | `SUPERPOWERS.md`, `docs/04-superpowers/`       |
| Project Harness | Skill Forge-specific constraints                  | `AGENTS.md`, `openspec/config.yaml`            |

## 5. Repository Layout (governance-relevant)

- `AGENTS.md` — universal entry.
- `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md` — tool-specific entries.
- `openspec/config.yaml` — OpenSpec config. Sets `schema: skill-forge-governance`. Contains project context and per-artifact rules.
- `openspec/schemas/skill-forge-governance/` — project-local schema: `schema.yaml`, `README.md`, `templates/`.
- `openspec/changes/` — in-flight and archived OpenSpec changes.
- `openspec/specs/` — archived capability specs.
- `docs/00-project/` — phase reports (Phase 0 / Phase 1 / Phase 2 / ...).
- `docs/03-openspec/` — schema, change-workflow, and per-artifact guidelines.
- `docs/04-superpowers/` — this folder.
- `.superpowers/` — Superpowers project configuration (this folder's parent).

## 6. Forbidden-Path Map (for Superpowers)

Superpowers must never instruct an Agent to modify any of the following without an explicit, scoped, in-flight OpenSpec change that names the path:

- `src/**` — runtime code.
- `tests/**` — tests.
- `templates/**` — Jinja2 templates.
- `configs/**` — default config files.
- `pyproject.toml`, `uv.lock` — dependencies.
- `README.md`, `README.zh-CN.md` — user-facing docs.
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md` — Agent entry points.
- `openspec/config.yaml` — OpenSpec config (only the schema change can modify it).
- `openspec/schemas/**` — schema definitions (only a schema change can modify them).
- `docs/03-openspec/**` — schema documentation (only a docs change can modify them).
- `docs/00-project/governance-bootstrap-report.md` — Phase 0 report (frozen).
- `docs/00-project/governance-schema-verification-report.md` — Phase 1 report (frozen).

A change that needs to touch any of these must have an OpenSpec change whose `plan.md` lists the path in `## Allowed Paths`. Superpowers must surface this requirement to the Agent before any modification.

## 7. Skill Selection Defaults

The default skill selection for Skill Forge work is recorded in `.superpowers/skill-usage-policy.md`. The canonical reference is `docs/04-superpowers/skill-usage-policy.md`. Superpowers uses the canonical reference and falls back to the project-local file only when the canonical is unavailable.

## 8. Cross-References

- Universal entry: `../AGENTS.md`
- Schema overview: `../openspec/schemas/skill-forge-governance/README.md`
- Change workflow: `../docs/03-openspec/change-workflow.md`
- Skill usage policy (canonical): `../docs/04-superpowers/skill-usage-policy.md`
- Execution discipline: `../docs/04-superpowers/execution-discipline.md`
- Subagent policy: `../docs/04-superpowers/subagent-policy.md`
- Phase 0 report (frozen): `../docs/00-project/governance-bootstrap-report.md`
- Phase 1 report (frozen): `../docs/00-project/governance-schema-verification-report.md`
