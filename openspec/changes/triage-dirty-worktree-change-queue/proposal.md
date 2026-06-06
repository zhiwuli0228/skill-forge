# Proposal: triage-dirty-worktree-change-queue

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 6 (dirty worktree triage)
> Date: 2026-06-06

## Why

Phases 0-5 introduced a working OpenSpec governance stack
and shipped five governed changes, but the working tree
still carries a large pre-existing dirty worktree that
mixes already-archived changes, untracked source modules,
untracked specs, local tool directories, and design
notes. The dirty surface blocks the next agent from
starting a clean governed change and obscures the
recommended sequencing of future work. We need a
documentation-only triage change that classifies every
dirty entry, lists the recommended future changes, and
records which entries require a human decision, without
deleting, resetting, restoring, or cleaning the dirty
worktree.

## What Changes

- New governance capability
  `dirty-worktree-change-queue` that records the
  classification scheme and the change queue ledger.
- New OpenSpec change folder
  `openspec/changes/triage-dirty-worktree-change-queue/`
  with the standard eight governance artifacts
  (`.openspec.yaml`, `brainstorm.md`, `proposal.md`,
  `design.md`, `review.md`, `plan.md`, `tasks.md`,
  `verification.md`) plus
  `specs/dirty-worktree-change-queue/spec.md`.
- New top-level doc `docs/00-project/dirty-worktree-triage-report.md`
  that summarizes the triage.
- New top-level doc `docs/00-project/wip-disposition-matrix.md`
  that classifies every dirty entry into A (absorbed),
  B (candidate for future governed change), C (existing
  change needs reshape), D (candidate for discard), or
  E (requires user decision).
- New top-level doc `docs/00-project/change-queue.md`
  that lists the recommended future OpenSpec changes in
  priority order with a one-line description, the
  blocking dependency, and the expected effort.

## Capabilities

### New Capabilities

- `dirty-worktree-change-queue`: a governance
  capability that records the A/B/C/D/E classification
  scheme and the change queue ledger, so that future
  agents can read the queue and the matrix from a
  single spec.

### Modified Capabilities

None. The pre-existing capabilities in
`openspec/specs/*` are out of scope for this slice.
The dirty entries that look like modified capabilities
(see the WIP disposition matrix) will be re-evaluated
by the future change that adopts them.

### Removed Capabilities

None. The pre-existing capabilities are preserved as
drafts; no capability is retired by this slice.

## Impact

- Code: none. The phase is documentation-only. No
  source file, test file, schema, blueprint, template,
  config, or runtime code is modified.
- CLI: none. No CLI surface is added, removed, or
  changed.
- Schemas: none. No schema, config field, blueprint,
  validation rule, provenance field, or package
  metadata field is changed.
- Workspaces: existing Skill Forge workspaces are
  unaffected. The dirty worktree stays on disk; this
  phase records its disposition without acting on it.

## Non-Goals

- This change does not implement any feature in the
  dirty worktree. The recommended future changes in
  the change queue are proposals, not actions.
- This change does not delete, reset, restore, or
  clean the dirty worktree. Every dirty entry is
  preserved on disk.
- This change does not modify any pre-existing
  OpenSpec change folder (active or archived).
- This change does not modify any source code, test,
  template, config, script, or governance doc outside
  the strict-scope allowed-path list.
- This change does not introduce a `.gitignore` rule.
  The `.claude/` and `.codex/` directories remain
  untracked and are recorded in the matrix as
  `D` (candidate for discard) for a follow-up change.
- This change does not archive the Phase 3/4/5
  changes. Archiving is the start of a later phase.

## Risks

- [The matrix and the queue may drift from the actual
  dirty worktree over time] -> Mitigation: the
  verification.md is the source of truth; the matrix
  and the queue are generated from a one-time
  snapshot taken at the start of Phase 6, and any
  drift is recorded as a follow-up entry.
- [The recommended change queue order may not match
  the user's actual priorities] -> Mitigation: the
  queue records the recommended order and the
  blocking dependency, but it is advisory; the user
  can reorder it.
- [The strict-scope allowed-path list may exclude a
  file the user wants to add to the matrix] ->
  Mitigation: the matrix lives entirely in
  `docs/00-project/wip-disposition-matrix.md` and is
  a plain markdown table; the user can extend it
  without touching any other file.

## Rollback

1. Delete the OpenSpec change folder
   `openspec/changes/triage-dirty-worktree-change-queue/`.
2. Delete the three new doc files
   `docs/00-project/dirty-worktree-triage-report.md`,
   `docs/00-project/wip-disposition-matrix.md`, and
   `docs/00-project/change-queue.md`.
3. The dirty worktree is unaffected. No code, test,
   template, config, or pre-existing OpenSpec change
   is touched, so rollback is a pure file delete.

## Consistency With Brainstorm

- Brainstorm file: `brainstorm.md`
- Recommended option: **Option A** (single triage
  change with three doc artifacts).
- Deviations and reasons: none. The proposal follows
  the brainstorm recommendation. The two non-blocking
  open questions (`.claude/.codex` inclusion and the
  follow-up docs commit) are deferred to the user;
  this phase records the recommended answer in the
  matrix and the verification, but does not bind the
  user to it.
