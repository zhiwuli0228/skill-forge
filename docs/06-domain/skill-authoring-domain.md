# Skill Authoring Domain

## Purpose

This document defines the Skill Forge domain: the Skill package concept, the inputs to skill authoring, the role of the blueprint, the template, the validator, and provenance, the expectations for the generated artifact, and the rules for deterministic generation.

## Scope

- Applies to: everything that produces, validates, or persists a `SKILL.md` package.
- Owns: the Skill package concept, the authoring pipeline, the generated artifact shape, and the determinism rules.
- Does **not** own: the lifecycle recommendation rules (see `lifecycle-rules.md`), the CLI surface (see `docs/01-architecture/module-boundaries.md`), or the OpenSpec governance mechanics (see `docs/03-openspec/`).

## Current Rules

### 1. The Skill Package Concept

A Skill package is a directory that contains at least `SKILL.md` and may contain a `skill-forge.json` provenance file, an `eval-report.json` eval record, and blueprint-declared attachments. The package is the unit of authoring, validation, evaluation, installation, upgrade, and lifecycle management.

A Skill package is **not**:

- A directory of arbitrary files. The `SKILL.md` is mandatory; everything else is opt-in by blueprint.
- A single Markdown file with a fixed name. The package directory can be moved, renamed, and re-installed without renaming the `SKILL.md` inside.
- A compiled artifact. The package is human-readable text; there is no bytecode, no binary, and no encrypted form.

The Skill package is the contract between Skill Forge and the target platform (Codex, opencode, Claude Code). The platform's job is to read `SKILL.md` and to follow its instructions. Skill Forge's job is to produce a `SKILL.md` that an AI agent can use.

### 2. Skill Authoring Inputs

The authoring pipeline accepts, in order:

1. **Requirement string.** A natural-language description of what the Skill should do. The string is the primary user input to the `create` command.
2. **Project context (optional).** When `--project <path>` is supplied, Skill Forge reads supported rule files under that path (`AGENTS.md`, `CLAUDE.md`, `README.md`, `.opencode/`, `.claude/`, `.agents/`, `openspec/`) and converts them into generation constraints. Project context is injected, not replacing the requirement.
3. **Blueprint (optional, automatic or explicit).** When the analyzer detects a supported task type, the matching built-in blueprint is applied. The user can also select a blueprint explicitly with `--blueprint <id>`. Custom blueprints are loaded from `~/.skill-forge/blueprints/` and from `<project>/.skill-forge/blueprints/`.
4. **LLM refinement (opt-in).** When `--llm` is supplied and the LLM is configured, the requirement is refined into structured fields. LLM output is merged only into supported structured fields; the original requirement is preserved as the source of truth.

The default path is **deterministic**: the requirement is the only required input, no project context, no LLM.

### 3. Blueprint Role

A blueprint is a named, reusable definition of a Skill's purpose, structure, and optional attachments. Blueprints live in three places:

- Built-in blueprints under `src/skill_forge/blueprints/builtin/`.
- User-level custom blueprints under `~/.skill-forge/blueprints/`.
- Project-level custom blueprints under `<project>/.skill-forge/blueprints/` (loaded only when `--project` is supplied).

A blueprint declares:

- The Skill's purpose, scope, and required sections.
- The default frontmatter (`name`, `description`).
- The list of attachments to render alongside `SKILL.md` (e.g., a `references/diagnosis-checklist.md`).
- Optional LLM usage hints.
- Optional quality gates that the validator enforces.

The blueprint is the source of structure; the requirement is the source of content. The generator renders the blueprint's structure with the requirement's content, fills the frontmatter, and writes the attachments. The blueprint is **not** a template literal; the generator renders it through Jinja2 with the requirement, the project context, and the LLM-refined fields as variables.

### 4. Template Role

A template is a Jinja2 file that renders a section of the Skill package. Templates live under `templates/` (e.g., `templates/common/SKILL.md.j2` for the default Skill template). Templates are the rendering layer; they are not the source of structure (the blueprint is) and they are not the source of content (the requirement is).

Templates must be deterministic: same input, same output. A template that depends on `time`, `random`, or environment variables is invalid. The validator may reject a generated package whose `SKILL.md` differs from a fresh render of the same inputs.

### 5. Validation Role

The validator runs static checks on a generated Skill package. It produces a `ValidationResult` with three lists:

- **Errors** — blocking. The package cannot be installed or evaluated when errors are present.
- **Warnings** — non-blocking. The package can be installed, but the author should review the warning. Authoring lint warnings are part of this list.
- **Suggested fixes** — deterministic text suggestions. The CLI prints them after a `validate` run. Suggestions are advisory; the validator does not modify files.

The validator must be **pure**: no file writes, no DB writes, no LLM calls, no network. The validator must produce the same result for the same package, regardless of when or where it runs.

### 6. Provenance Role

Provenance is the bounded record of how a Skill package was produced. It lives in `skill-forge.json` next to `SKILL.md`. Provenance is mandatory for any package produced by `create` and is the only reliable input to `upgrade`. A package without `skill-forge.json` cannot be upgraded because the upgrade path cannot reconstruct the original requirement and blueprint source.

Provenance records:

- `schema_version` — the provenance schema version. Bumped on shape change.
- `generated_at` — ISO 8601 UTC timestamp.
- `requirement` — the original requirement text.
- `target_platform` — the platform the package was authored for (`codex`, `opencode`, `claude`).
- `language` — the default language for the package body.
- `blueprint` — the blueprint id, or `null` for the default blueprint.
- `llm_used` — `true` if `--llm` was used, `false` otherwise.
- `llm_model` — the model name when `llm_used` is `true`, `null` otherwise.
- `project_path` — the project path when `--project` was used, `null` otherwise.
- `quality_score` — the quality report's score at generation time.
- `attachments` — the list of generated attachment paths relative to the package root.

The `skill-forge.json` schema is owned jointly by the storage layer (the writer) and the `models/` layer (the Pydantic model). A change to the schema is a breaking change and requires an OpenSpec change.

### 7. Eval Report Role

The eval report is the latest deterministic eval run summary. It lives in `eval-report.json` next to `SKILL.md`. The eval runner is the only writer; the eval report is read by the `show` command and by the upgrade path.

The eval report records:

- `schema_version` — the eval report schema version.
- `ran_at` — ISO 8601 UTC timestamp.
- `case_count`, `passed`, `failed` — counts.
- `cases` — per-case result with assertion-level details.

### 8. Generated Artifact Expectations

A generated Skill package must satisfy:

- A `SKILL.md` with frontmatter containing `name` and `description`.
- `name` matches the package directory name. The validator warns on a mismatch.
- The body includes the sections declared by the blueprint (default: Purpose, When to use, When not to use, Required inputs, Workflow, Constraints, Output format, Quality gates).
- The body is plain Markdown. No embedded HTML, no script tags, no executable code.
- The frontmatter `name` is a slug (`a-z`, `0-9`, `-`); the validator warns on uppercase, spaces, or non-slug characters.
- The package directory is the unit of move / rename / install. The CLI does not modify the package on `install`; install is a copy.

### 9. Rules for Deterministic Generation

The default generation path must be deterministic. The following rules are non-negotiable:

- Same requirement + same blueprint + same project context → same `SKILL.md` (byte-for-byte, modulo `generated_at` in provenance).
- No random sampling in the generator. If the requirement is ambiguous, the generator picks the first match, not a random one.
- No time-dependent content in `SKILL.md`. The `generated_at` timestamp lives in `skill-forge.json`, not in `SKILL.md`.
- No environment-dependent content. The LLM refiner is opt-in; the default path does not consult it.
- No network calls in the default path. The corpus and the LLM are the only optional network surfaces, and both are explicit.
- The generator must be reproducible from provenance. The `upgrade` command reconstructs the requirement and the blueprint id from `skill-forge.json` and re-renders. If the generator cannot reproduce a previous package from its provenance, the upgrade is unsupported.

### 10. What a Generated Skill Is For

A generated Skill is for an AI agent on a target platform to read. The agent reads the `SKILL.md`, follows the Workflow section, applies the Constraints, and produces the Output format. The Quality gates section is a self-check the agent runs before declaring the work done.

A generated Skill is **not** for a human to read end-to-end. The human reads the frontmatter, the Purpose, the Workflow, and the Quality gates. The body is structured for the agent's consumption, not for narrative reading.

## Related Files

- `docs/06-domain/lifecycle-rules.md` — lifecycle recommendation semantics.
- `docs/01-architecture/architecture-overview.md` — layer model.
- `docs/01-architecture/data-flow.md` — creation and validation flows.
- `docs/01-architecture/module-boundaries.md` — which module owns the requirement analyzer, blueprints, generator, validator.
- `src/skill_forge/requirement/`, `src/skill_forge/blueprints/`, `src/skill_forge/generator/`, `src/skill_forge/validator/`, `src/skill_forge/library/`, `src/skill_forge/evals/` — authoring components.
- `templates/common/SKILL.md.j2` — the default Skill template.
- `configs/sources.yaml` — the default research sources.
- `README.md` — user-facing quick start and command reference.

## What Not To Do

- Do not produce a Skill package without `SKILL.md`. The file is mandatory.
- Do not inject free-form LLM text into `SKILL.md`. LLM output is merged only into supported structured fields.
- Do not call the LLM from the default `create` flow. LLM is opt-in via `--llm`.
- Do not write a generated `SKILL.md` that depends on `time`, `random`, or environment variables. The default path is deterministic.
- Do not change the `skill-forge.json` schema without an OpenSpec change. The schema is part of the public contract.
- Do not let the validator write files, call the LLM, or hit the network. The validator is pure.
- Do not let the upgrade path reconstruct a requirement from anywhere other than `skill-forge.json`. Provenance is the source of truth.
- Do not embed executable code, scripts, or HTML in `SKILL.md`. The body is plain Markdown.
