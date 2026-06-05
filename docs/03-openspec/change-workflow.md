# Change Workflow

This document describes the lifecycle of an OpenSpec change under the `skill-forge-governance` schema, from creation to archive. It is the canonical workflow reference; the per-artifact guidelines in this folder cover the content of each artifact.

## 1. Lifecycle Overview

A change moves through five status states and produces eight artifacts.

```text
draft  ->  ready-for-review  ->  approved  ->  applying  ->  done
```

The eight artifacts are produced in the order:

```text
brainstorm  ->  proposal  ->  spec  ->  design  ->  review  ->  plan  ->  tasks  ->  verification
```

The status transitions are tied to artifacts, not to wall-clock time. A change is `ready-for-review` only when proposal, spec, design, and review are all written. A change is `approved` only when the review verdict is `approve`. A change is `done` only when verification.md is written and `openspec validate --strict` passes.

## 2. State Transitions

### 2.1 `draft`

The change has been created (`openspec new --change <id>`) and the drafter is producing artifacts. The drafter is typically Codex, but may be any agent that has read `AGENTS.md`, `CODEX.md`, and the schema.

- Required artifacts so far: none.
- Allowed: writing any artifact, in any order, in the `draft` state.
- Block: cannot be archived from `draft`.

### 2.2 `ready-for-review`

The drafter signals the change is ready for review by writing `review.md` and setting its verdict. The review is the gate; the drafter does not declare the change `ready-for-review` lightly.

- Required artifacts: `proposal.md`, `specs/<capability>/spec.md` (one or more), `design.md`, `review.md`.
- The review verdict is one of `approve`, `request-changes`, `block`.
- Block: cannot move to `approved` without verdict `approve`.

### 2.3 `approved`

The review verdict is `approve`. The implementation agent may now produce `plan.md` and `tasks.md`.

- Required artifacts: those of `ready-for-review`, plus `plan.md`.
- The drafter is responsible for ensuring the plan is consistent with the review.
- Block: cannot move to `applying` without `plan.md`.

### 2.4 `applying`

The implementation agent is working through `tasks.md`. Each completed task is marked `- [x]`. The implementation agent pauses and reports when:

- A task would require touching a forbidden path.
- A verification command cannot run for non-environmental reasons.
- The actual file list differs from the planned file list.
- The plan and the repository state disagree in a way that affects the diff.

- Required artifacts: those of `approved`, plus a partially or fully completed `tasks.md`.
- Allowed: only the implementation agent should write to `tasks.md` and (later) `verification.md`. Other agents should not.

### 2.5 `done`

All tasks are complete, `verification.md` is written, and `openspec validate <change-id> --strict` passes. The change is archiveable.

- Required artifacts: all eight.
- Verdict in `verification.md` is `done` or `done-with-risks`.
- `openspec validate --strict` returns `valid`.

## 3. Branching

OpenSpec allows multiple changes in `openspec/changes/` at the same time. A change does not need to be `done` before another change is started. Branches in the version control system are not required for change branching; the change folder is the unit.

When two changes would touch the same file, the implementer of the second change must:

1. Re-read the first change's `proposal.md`, `spec.md`, and `design.md`.
2. Update their own `proposal.md` `## Impact` section to call out the overlap.
3. Either land the first change first, or coordinate the merge in `verification.md` of the second change.

## 4. Archive

When a change is `done`, archive it:

```bash
openspec archive <change-id>
```

`archive` moves the change folder under `openspec/changes/archive/<date>-<change-id>/` and merges the change's `ADDED Requirements` into the corresponding files in `openspec/specs/`. The change folder is then read-only.

If `openspec validate --strict` does not pass, `archive` fails. The change is not archived.

## 5. Rollback

If a change is `done` and later found broken, the recovery depends on whether it has been archived.

- Not archived: revert the change folder to `draft`, update the change, and re-apply.
- Archived: create a new change that REMOVES the offending requirements from the corresponding `openspec/specs/<capability>/spec.md`. Do not rewrite history; add a new change that explains the rollback.

## 6. Worked Example

A minimal worked example, with the artifacts a real change would produce, is maintained as a working change under `openspec/changes/<example-id>/`. Refer to it for the expected shape of each artifact.

## 7. Cross-References

- Per-artifact content rules: see `artifact-rules.md`.
- Schema policy and schema-vs-package defaults: see `schema-policy.md`.
- Per-artifact writing guidance:
  - `proposal-guidelines.md`
  - `spec-guidelines.md`
  - `design-guidelines.md`
  - `task-guidelines.md`
