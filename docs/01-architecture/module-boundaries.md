# Module Boundaries

## Purpose

This document names the modules under `src/skill_forge/`, declares which module owns which concern, and states the rules for crossing — or, more importantly, not crossing — module boundaries.

## Scope

- Applies to: code under `src/skill_forge/`, with cross-references to `templates/`, `configs/`, and `openspec/specs/`.
- Owns: module ownership, dependency direction, and the rules for adding a new module.
- Does **not** own: layer model (see `architecture-overview.md`), per-flow sequencing (see `data-flow.md`), or domain semantics (see `docs/06-domain/`).

## Current Rules

### 1. Module Ownership

| Module | Owns | May import from | Must not import from |
|---|---|---|---|
| `cli.py` | Typer command surface, output formatting, exit codes | any module | — |
| `config.py` | Workspace config, environment variable resolution, default paths | `storage/paths` | CLI, services |
| `storage/` | Local SQLite, file-system paths, corpus file layout, drafts, blueprint files | `models/`, `config.py` | CLI, services, templates |
| `models/` | Pydantic models, enums, typed contracts, provenance shapes | nothing internal | any other module |
| `requirement/` | Rule-based requirement parsing from natural language | `models/` | blueprints, generator, CLI |
| `blueprints/` | Built-in and custom blueprint loading and enriching | `models/`, `config.py` | generator, CLI, retrieval |
| `generator/` | Jinja2 template rendering, `SKILL.md` generation, `skill-forge.json` provenance write | `models/`, `blueprints/`, `requirement/`, `storage/`, `config.py` | CLI, validator, retrieval |
| `validator/` | Static validation of generated Skill packages, lint warnings, suggested fixes | `models/`, `storage/paths` | generator, CLI, retrieval |
| `library/` | List, show, diff, upgrade, eval-report persistence for generated packages | `models/`, `storage/`, `validator/` | CLI, retrieval, requirement |
| `evals/` | Deterministic local eval case runner | `models/`, `library/`, `validator/` | CLI, retrieval, requirement |
| `upgrade/` | Upgrade candidate generation from provenance + current blueprint | `models/`, `blueprints/`, `library/`, `storage/` | CLI, retrieval |
| `research/` | Research corpus update from configured sources | `models/`, `storage/`, `config.py` | CLI, requirement, validator |
| `retrieval/` | TF-IDF search, offline rerank, retrieval-augmented generation | `models/`, `research/`, `storage/` | CLI, requirement, generator, validator |
| `project_context/` | Reads `AGENTS.md`, `CLAUDE.md`, `openspec/`, `.opencode/`, `.claude/`, `.agents/` and converts them into generation constraints | `models/`, `config.py` | generator, CLI |
| `interaction/` | Interactive draft save and resume | `models/`, `requirement/`, `blueprints/`, `storage/` | CLI, validator, retrieval |
| `installer/` | Platform adapter that places a generated Skill into Codex, opencode, or Claude directories | `models/`, `storage/`, `config.py` | generator, validator, retrieval |
| `lifecycle/` | Pure lifecycle recommendation rules, service adapter, promotion, rollback, lifecycle state models | `models/`, `storage/` | CLI, retrieval, generator, requirement |
| `adoption/` | Adopt a cached corpus Skill document into the local Skill library | `models/`, `library/`, `retrieval/`, `storage/` | CLI, generator, validator, requirement |
| `experience/` | Experience accumulation, experience model, experience service | `models/`, `storage/`, `llm/` | CLI, generator, validator, retrieval |
| `llm/` | Optional LLM refiner and structured-field generation | `models/`, `config.py` | CLI, generator, validator, retrieval, storage (writes) |
| `lifecycle/recommendation.py` | Pure recommendation rules (no I/O) | `models/lifecycle` only | anything that imports from `storage/`, `retrieval/`, `cli`, services |

The default direction of dependency is **downward and inward** toward `models/`. A module that owns a higher-level concern (CLI, services) may import from a module that owns a lower-level concern. A module that owns a lower-level concern must not import from a higher-level concern.

### 2. Lifecycle Recommendation Ownership

The lifecycle recommendation rules are the only subsystem that is allowed to be split between two files: a pure rules file and a service adapter.

- `src/skill_forge/lifecycle/recommendation.py` — **pure rules**. No I/O, no database, no network, no LLM, no storage, no logging that touches a handler. Inputs are typed Pydantic models; outputs are typed Pydantic models. This is a hard rule, not a guideline, because the recommendation rules are reused in tests, in service adapters, and (eventually) in alternative front-ends.
- `src/skill_forge/lifecycle/service.py` — **service adapter**. Owns the orchestration that calls the pure rules. Owns the storage read/write, the user output, and the wire format. May import from `retrieval/`, `storage/`, `models/`. May not import from `cli/`.
- `src/skill_forge/lifecycle/promotion.py` — **promotion and rollback** logic. Owns the state transitions for active Skill packages. May import from `models/`, `storage/`, `validator/`. Must not import from `cli/`.

### 3. Validation Ownership

`validator/` owns the static checks applied to a generated Skill package. It produces a `ValidationResult` with errors, warnings, and deterministic suggested fixes. It must not produce side effects (no file writes, no DB writes). It must not call into the LLM. It must not import from `generator/`, `retrieval/`, or `cli`.

### 4. Retrieval and Search Ownership

`retrieval/` owns TF-IDF ranking, optional offline rerank, and the retrieval-augmented generation path used by `add-intelligent-generation-fallback`. It reads from the local corpus built by `research/`. It must not write to the corpus. It must not import from `cli/`, `requirement/`, `generator/`, or `validator/`.

### 5. Storage and Provenance Ownership

`storage/` owns the local workspace layout, the SQLite metadata database, the corpus file layout, the drafts directory, the blueprint files, and the path resolution. It is the only module allowed to write the on-disk provenance shape (`skill-forge.json`, `eval-report.json`). The shape of those files is owned jointly with `models/` (the Pydantic models), but the act of writing them is owned by `storage/` or by the subsystem that called storage (`library/`, `evals/`, `upgrade/`).

### 6. CLI Surface Ownership

`cli.py` is the only module allowed to:

- Define a Typer command.
- Print to stdout for user-facing output.
- Set a process exit code based on a service result.
- Resolve `SKILL_FORGE_HOME` indirectly through `config.py`.

`cli.py` is **not** allowed to:

- Contain business logic. Every command delegates to a service.
- Import from `models/` except for type annotations.
- Read from or write to the workspace directly. All I/O flows through a service.

### 7. Rules for Crossing Boundaries

- A module may call a service in another module. It may not call a service in two layers above itself.
- A module may not re-export a model from another module's namespace. Imports must point at the defining module.
- A module that owns a Pydantic model is the only module allowed to validate, parse, or serialize instances of that model. Other modules convert their inputs into the owning module's models at the boundary.
- Circular imports are forbidden. Resolve them with a late import inside a function or with a small `protocols.py` shim.

### 8. Rules for Adding a New Module

- New modules require a non-trivial OpenSpec change that names the module's owner, allowed imports, and forbidden imports.
- The new module must be added to the table in Section 1.
- The new module must declare its public surface in `__init__.py` and keep all internal helpers private (leading underscore).
- The new module must ship with at least one test file under `tests/` that exercises the public surface.

## Related Files

- `docs/01-architecture/architecture-overview.md` — layer model.
- `docs/01-architecture/data-flow.md` — how requests move through the modules.
- `docs/06-domain/lifecycle-rules.md` — lifecycle recommendation semantics.
- `src/skill_forge/cli.py` — the only CLI entry point.
- `src/skill_forge/models/` — the domain model.
- `openspec/specs/` — capability-level contracts that the modules implement.

## What Not To Do

- Do not put business logic in `cli.py`. Commands are thin orchestrators.
- Do not let `models/` import from any runtime module. Models are leaves in the dependency graph.
- Do not let `validator/` call the LLM, write to disk, or import from `generator/`.
- Do not let `retrieval/` write to the corpus. Corpus writes belong to `research/`.
- Do not put I/O inside `lifecycle/recommendation.py`. The recommendation rules are pure.
- Do not import from `cli/` in any runtime module.
- Do not add a module without an OpenSpec change.
- Do not split a single concern across two modules when a single module with clear internal helpers is sufficient.
