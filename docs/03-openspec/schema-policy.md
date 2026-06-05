# Schema Policy

This document defines the policy for managing the `skill-forge-governance` schema. It covers what the schema owns, what it does not own, how it relates to the default `spec-driven` schema, and how schema changes are made.

## 1. What the Schema Owns

The schema owns:

- The **structure** of each change artifact (headings, sections, required content).
- The **order** in which artifacts are produced.
- The **dependency graph** between artifacts (the `requires:` field).
- The **verification semantics** for the change as a whole (via `apply:`).
- The **templates** that agents start from when writing each artifact.

The schema is enforced by OpenSpec's `validate` command. A change that does not match the schema cannot be archived.

## 2. What the Schema Does NOT Own

The schema does not own:

- The **content** of a Skill Forge skill or feature. That is the responsibility of the spec, design, and code, not the schema.
- The **execution discipline** for implementation. That is owned by Superpowers (TDD, debugging, verification) and the project entry points (`AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `OPENCODE.md`).
- The **Skill Forge-specific constraints** (local-first, deterministic generation, etc.). Those are owned by the Project Harness and recorded in `openspec/config.yaml` under `context:` and `rules:`.
- The **runtime code** under `src/`, `tests/`, `templates/`, `configs/`. The schema is documentation; the code is the implementation.

When in doubt, the schema is the structure, not the content.

## 3. Relationship to the Default `spec-driven` Schema

The default `spec-driven` schema is bundled with the OpenSpec CLI. It produces four artifacts in this order:

```text
proposal -> specs -> design -> tasks
```

The `skill-forge-governance` schema is a project-local extension. It produces eight artifacts in this order:

```text
brainstorm -> proposal -> spec -> design -> review -> plan -> tasks -> verification
```

The two schemas agree on proposal, spec(s), design, and tasks. They differ in:

- `skill-forge-governance` adds `brainstorm` (before proposal) for problem clarification.
- `skill-forge-governance` adds `review` (between design and plan) for cross-artifact consistency.
- `skill-forge-governance` adds `plan` (between design/review and tasks) for the executable contract.
- `skill-forge-governance` adds `verification` (after tasks) for the evidence record.
- `skill-forge-governance` uses singular `spec` (one file per capability) rather than plural `specs` (the spec-driven convention), to make the change folder layout explicit.

A change started under `spec-driven` cannot be migrated to `skill-forge-governance` mid-flight. A new change must be started under the target schema.

## 4. Selection

The schema is selected by setting `schema: skill-forge-governance` in `openspec/config.yaml`. There is one schema per project. The `skill-forge-governance` schema is the only schema in use.

If a future need arises for a different schema, the policy is:

1. Open a change to introduce the new schema, with the new schema's `schema.yaml`, `README.md`, and `templates/`.
2. Update `openspec/config.yaml` only after the new schema's `openspec schema validate` passes.
3. Do not delete `skill-forge-governance/` until all in-flight changes under it are archived.

## 5. Modifying the Schema

Schema files are versioned. The current version is `1`, recorded in `schema.yaml`. A schema change is itself a change under OpenSpec. The change:

- Must include a `proposal.md` that explains the schema change and its impact on existing changes.
- Must include a `specs/schema/schema.md` (or similar) that documents the new artifact shape.
- Must include a `design.md` that covers template content and the `requires:` graph.
- Must include a `review.md` with verdict `approve`.
- Must include a `verification.md` that records the result of `openspec schema validate skill-forge-governance --verbose`.
- Bumps the `version:` field in `schema.yaml`.

A schema change is allowed to modify the `templates/` directory, the `schema.yaml` definition, and the `README.md` overview. It is NOT allowed to modify `openspec/config.yaml` (that is a different change) or to rename artifacts (that would break all in-flight changes).

## 6. Schema Validation

The schema is validated by OpenSpec. The relevant commands are:

```bash
openspec schema validate skill-forge-governance
openspec schema validate skill-forge-governance --verbose
openspec schema validate skill-forge-governance --json
```

`openspec schema validate` checks:

- The `schema.yaml` is parseable YAML.
- Each `templates/<artifact>.md` referenced from `schema.yaml` exists.
- The `requires:` graph is a DAG (no cycles).
- The `apply:` block is consistent with the artifacts.

Validation must pass before a schema change is archived. Validation is a Phase 1 verification step; see `docs/00-project/governance-schema-verification-report.md`.

## 7. Failure Modes

The following are explicit failure modes and how they are handled:

- A template is missing: `openspec schema validate` fails with a clear error. The schema change cannot be archived.
- An `instruction` field is empty: `openspec schema validate` warns. The schema change can still be archived, but a follow-up should be filed.
- Two artifacts have the same `generates` pattern: `openspec schema validate` fails. The schema change cannot be archived.
- A `requires:` field references an unknown artifact: `openspec schema validate` fails.
- The schema version is not bumped after a structural change: caught by the review step.

## 8. Cross-References

- Per-artifact guidelines:
  - `proposal-guidelines.md`
  - `spec-guidelines.md`
  - `design-guidelines.md`
  - `task-guidelines.md`
- Artifact content rules: `artifact-rules.md`.
- Change lifecycle: `change-workflow.md`.
