# Architecture Overview

## Purpose

This document is the **current architecture authority** for Skill Forge. It defines the system as a local-first CLI workspace for AI agent Skill generation, validation, installation, and lifecycle governance, and names the architectural layers, their responsibilities, and the boundaries that must remain stable.

## Scope

- Applies to: the entire `skill-forge` repository.
- Owns: the layer model, the role of governance in the architecture, and the architectural invariants that other docs and code must respect.
- Does **not** own: per-module internals (see `module-boundaries.md`), per-flow sequencing (see `data-flow.md`), domain rules (see `docs/06-domain/`), or governance mechanics (see `docs/03-openspec/`).

## Current Rules

### 1. Skill Forge Is a Local-First CLI Workspace

Skill Forge runs as a single user-invoked CLI process. There is no server, no background daemon, and no remote control plane. The default workspace is `~/.skill-forge/`. Every command must be safe to run on a developer laptop with no network access and no database server. The CLI may call out to an LLM only when the user explicitly opts in (`--llm`).

### 2. Architectural Layers

The system is organized as seven layers. Each layer talks to the layer below it through a small, named boundary; horizontal shortcuts between layers are forbidden.

| Layer | Owns | Lives in (typical) |
|---|---|---|
| CLI layer | Typer command surface, argument parsing, output formatting | `src/skill_forge/cli.py` |
| Application / service layer | Orchestration, command flows, side-effect coordination | `src/skill_forge/<feature>/service.py` |
| Domain / model layer | Pydantic models, invariants, typed contracts | `src/skill_forge/models/` |
| Template / rendering layer | Jinja2 templates, blueprint definitions, rendering | `src/skill_forge/generator/`, `src/skill_forge/blueprints/`, `templates/` |
| Validation layer | Static checks on generated Skill packages | `src/skill_forge/validator/` |
| Storage / provenance layer | Local SQLite, corpus files, drafts, blueprint files, `skill-forge.json` provenance | `src/skill_forge/storage/`, `src/skill_forge/research/`, `src/skill_forge/library/` |
| Governance layer | OpenSpec/SuperSpec change lifecycle, agent entry points, scope rules, Superpowers discipline | `openspec/`, `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, `SUPERPOWERS.md`, `docs/03-openspec/`, `docs/04-superpowers/` |

The governance layer is a peer of the runtime layers, not a wrapper around them. It dictates *what may change* and *under what process*; the runtime layers dictate *how a Skill is produced and managed*.

### 3. Core Subsystems

The runtime layers compose into five subsystems that a user can name from the CLI:

- **Skill generation** — natural-language requirement → `SkillRequirement` → Jinja2 render → `GeneratedSkillPackage` (`src/skill_forge/requirement/`, `src/skill_forge/blueprints/`, `src/skill_forge/generator/`).
- **Validation** — `GeneratedSkillPackage` → `ValidationResult` with errors, warnings, and deterministic suggested fixes (`src/skill_forge/validator/`).
- **Library management** — listing, showing, diffing, upgrading, and evaluating generated Skill packages; writing `skill-forge.json` provenance and `eval-report.json` (`src/skill_forge/library/`, `src/skill_forge/evals/`, `src/skill_forge/upgrade/`).
- **Retrieval and search** — local research corpus update, TF-IDF search, optional offline rerank, project-context injection (`src/skill_forge/research/`, `src/skill_forge/retrieval/`, `src/skill_forge/project_context/`).
- **Installation and lifecycle** — platform adapter that places a generated Skill into Codex, opencode, or Claude directories; lifecycle recommendation, promotion, and rollback (`src/skill_forge/installer/`, `src/skill_forge/lifecycle/`, `src/skill_forge/adoption/`, `src/skill_forge/experience/`).

### 4. Role of OpenSpec, SuperSpec, and Superpowers

OpenSpec is the lifecycle authority for changes. It decides whether a change exists, what its scope is, and when it is archived. The `skill-forge-governance` schema defines the eight required artifacts per change (`.openspec.yaml`, `brainstorm`, `proposal`, `spec`, `design`, `review`, `plan`, `tasks`, `verification`).

SuperSpec-style artifacts are the structured content of an OpenSpec change — the spec deltas, the design decisions, the task list, the plan, the verification record. They are the inputs to implementation, not the implementation itself.

Superpowers is the execution discipline. It owns *how* the implementation runs: which skill to invoke at which phase, when to follow TDD, how to debug, what evidence to record before declaring done. Superpowers never overrides `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, or any `openspec/` decision.

The Project Harness (`AGENTS.md`, `CLAUDE.md`, `docs/`) is the Skill Forge-specific constraint layer. It names paths, schemas, and semantics that the methodology layers must respect.

### 5. What Must Remain Stable

The following invariants are architecture-level and must not change without a non-trivial OpenSpec change that explicitly proposes a replacement:

- The seven-layer model and the direction of dependency (top-down only; no horizontal shortcuts).
- The Pydantic-based domain model with `extra="forbid"` semantics for all stored artifacts.
- The provenance contract: every generated Skill package carries a `skill-forge.json` that records the schema version, generation time, original requirement, target platform, language, applied blueprint, LLM usage, project path, quality score, and generated attachment paths.
- The CLI command surface and the public model names — changes here are breaking and require a deprecation note in the change's `proposal.md`.
- The OpenSpec change artifact set: eight required artifacts per change under `openspec/changes/<change-id>/`.
- The Agent entry-point set: `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md` are required for any non-trivial change.
- The governance directory layout: `openspec/`, `docs/03-openspec/`, `docs/04-superpowers/` are the only governance authorities.

## Related Files

- `docs/01-architecture/module-boundaries.md` — which module owns what.
- `docs/01-architecture/data-flow.md` — how a request moves through the layers.
- `docs/03-openspec/change-workflow.md` — OpenSpec lifecycle and artifact rules.
- `docs/04-superpowers/superpowers-overview.md` — Superpowers positioning and phase mapping.
- `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`, `SUPERPOWERS.md` — agent entry points.
- `src/skill_forge/cli.py` — the CLI surface.
- `openspec/config.yaml` — project-level OpenSpec context and rules.

## What Not To Do

- Do not add a server, background daemon, scheduled job, or remote control plane. The system is local-first.
- Do not introduce a runtime dependency on a network service other than the optional, user-enabled LLM call.
- Do not change the layer direction. A model must not import from a service. A service may import from a model. A CLI command may call a service but must not import a model directly except to type-annotate.
- Do not add a new public CLI command, a new stored artifact format, or a new lifecycle phase without an OpenSpec change.
- Do not move a runtime concern into the governance layer or a governance concern into the runtime layers. They are peers.
- Do not rename or repurpose the Agent entry points (`AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md`).
- Do not introduce a second schema for OpenSpec changes. `skill-forge-governance` is the only schema.
