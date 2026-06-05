# Design: example-governance-stack-walkthrough

> Status: example
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md
>
> **EXAMPLE ONLY.** This design does not describe a real implementation.
> It is part of the example change `example-governance-stack-walkthrough`,
> which exists to demonstrate the full eight-artifact governance flow.
> The "implementation" described here is the creation of this example
> folder itself.

## Context

The Skill Forge governance stack is in place: `AGENTS.md` (Phase 0), `openspec/schemas/skill-forge-governance/` (Phase 1), and the `docs/03-openspec/` + `docs/04-superpowers/` + `.superpowers/` docs (Phase 2). What is missing is a worked example showing all eight artifacts in one place. This change provides that example.

The example is self-referential. The "implementation" is the example folder itself. No external file is modified.

## Goals / Non-Goals

### Goals

- Produce a complete example change folder with all eight artifacts.
- Demonstrate the schema's content rules for each artifact.
- Pass `openspec validate example-governance-stack-walkthrough --strict`.
- Be clearly marked as Example Only in every artifact.

### Non-Goals

- Do not modify any external file.
- Do not propose a real feature or fix.
- Do not invent a new schema field, lifecycle phase, agent role, or governance rule.

## Decisions

### Decision 1: Self-referential scope

- **Decision**: the example is contained in the folder `openspec/changes/example-governance-stack-walkthrough/`. No other path is touched.
- **Rationale**: an example that modifies external files is harder to recognize as an example. A self-referential example is unambiguous.
- **Alternatives considered**:
  - "Add a Cross-Reference Footer to `docs/04-superpowers/superpowers-overview.md`" — rejected because the change would actually do work, blurring the line between example and real change.
  - "Add an example subsection to `docs/03-openspec/`" — rejected because the example would not exercise the OpenSpec change pipeline, defeating the purpose.

### Decision 2: Mark every artifact with `> Status: example` and `> **EXAMPLE ONLY.**`

- **Decision**: every artifact file starts with a status line and an example-only notice, before the first `## Section`.
- **Rationale**: a reader who skims the file's first ten lines must be able to tell it is an example without reading further.
- **Alternatives considered**:
  - "Put the marker in the file name" — rejected because file names are not a reliable place for status metadata.
  - "Put the marker in the change folder name" — rejected because folder names are part of the path that the schema validates; changing the schema is out of scope.

### Decision 3: Use the existing schema's templates as the structural backbone

- **Decision**: every artifact follows the section structure of the corresponding template under `openspec/schemas/skill-forge-governance/templates/`.
- **Rationale**: the example must validate under the schema. The templates are the contract. Inventing a new structure would either fail validation or invalidate the example as a teaching artifact.
- **Alternatives considered**:
  - "Use a simpler structure" — rejected because the example would not exercise the full template.

## Data Contracts

No data contracts change. The example does not modify any stored artifact schema (`skill-forge.json`, `eval-report.json`, `config.yaml`, blueprint schema, etc.).

## Module Boundaries

### Added

- `openspec/changes/example-governance-stack-walkthrough/` — the example change folder.

### Modified

- None.

### Untouched

- All other paths. The example is fully self-contained.

## Compatibility Impact

- Claude Code: no effect.
- Codex: no effect.
- opencode: no effect.
- Generated Skill packages: no effect.

## Offline and Deterministic Mode

- Network unavailable: no effect. The example is local.
- LLM disabled: no effect. The example does not invoke any LLM.
- LLM enabled but config missing: no effect. Same.

## Security and Filesystem

- Reads: only the schema's `templates/` files, by the drafter.
- Writes: only the new files inside `openspec/changes/example-governance-stack-walkthrough/`.
- Environment variables: none.

## Risks / Trade-offs

- A future drafter mistakes the example for a real change and tries to archive it -> Mitigation: every artifact is marked `> Status: example` and `> **EXAMPLE ONLY.**`.
- The example becomes stale as the schema evolves -> Mitigation: re-validate the example whenever the schema is bumped. A future phase should add a CI check.
- The example pollutes the `openspec validate --all` output -> Mitigation: this is acceptable; the example is short and clearly marked.

## Migration Plan

### Deploy

1. The change is deployed by committing the example folder under `openspec/changes/example-governance-stack-walkthrough/`.
2. No data migration. No user-facing change.

### Rollback

1. Delete the folder `openspec/changes/example-governance-stack-walkthrough/`.
2. No other rollback is needed.

## Open Questions

- [non-blocking] Should the OpenSpec CLI offer a flag to exclude example changes from `openspec validate --all`? Not in scope. The example should always be valid.
- [non-blocking] Should the example be excluded from `openspec archive`? Not in scope. The example is never archived.
