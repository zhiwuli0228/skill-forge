# Skill Forge Documentation

This directory is the documentation entry point for Skill Forge.

## Directory Map

| Directory | Responsibility |
|---|---|
| `00-project/` | Project status, roadmap, reports, governance summaries, and change queue. |
| `01-architecture/` | Current architecture authority, module boundaries, data flow, and contracts. |
| `02-harness/` | Project-level AI Harness rules for AI-assisted development. |
| `03-openspec/` | OpenSpec and SuperSpec-style change governance rules. |
| `04-superpowers/` | Superpowers execution discipline and agent working methods. |
| `05-development/` | Local development, testing, dependency, and release workflow. |
| `06-domain/` | Skill Forge domain rules, lifecycle concepts, validation, provenance, and adapters. |
| `07-operations/` | Installation, runtime, security, maintenance, and troubleshooting. |
| `99-archive/` | Historical, superseded, or process-only documents. |

## Current Authority Model

Use this order when looking for project truth:

1. Root governance files: `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md`
2. `docs/00-project/` for current project status and queue
3. `docs/01-architecture/` for architecture
4. `docs/02-harness/` for AI-assisted development rules
5. `docs/03-openspec/` for change governance
6. `docs/04-superpowers/` for execution discipline
7. `docs/06-domain/` for product/domain behavior

## Placement Rules

- Do not place new documents directly under `docs/` unless they are top-level navigation files.
- Do not mix phase reports with architecture or domain authority.
- Do not move existing documents without a separate cleanup change.
- Historical documents should move to `99-archive/` only after they are replaced by current authority documents.

## Migrated Legacy Documents

After the Batch 1–3 documentation cleanup, all legacy root-level documents have been relocated:

- **Historical design drafts** now live under `docs/99-archive/old-designs/`.
- **Historical taskbooks** now live under `docs/99-archive/taskbooks/`.
- **Deferred roadmap documents** now live under `docs/00-project/deferred-roadmaps/`.
- **Release notes** live under `docs/00-project/release-notes.md`.
- **`docs/00-project/docs-classification-plan.md`** records the migration plan.
- **`docs/00-project/docs-cleanup-verification-report.md`** records the final cleanup verification.
