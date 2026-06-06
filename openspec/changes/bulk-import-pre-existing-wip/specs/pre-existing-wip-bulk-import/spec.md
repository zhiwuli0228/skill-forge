# Pre-Existing WIP Bulk Import Specification

> Status: draft
> Schema: skill-forge-governance
> Capability: `pre-existing-wip-bulk-import`
> File: `specs/pre-existing-wip-bulk-import/spec.md`
>
> This spec describes the bulk-slice governance that
> absorbs the A + B entries from the Phase 6 dirty
> worktree in a single OpenSpec change. The slice is
> mechanical: it adopts pre-existing dirty-worktree
> content verbatim, defers D + E classes, and pushes
> the commit(s) to `origin/main`.

## Purpose

Record the bulk-slice governance that absorbs the
A + B entries from the Phase 6 dirty worktree
(`docs/00-project/wip-disposition-matrix.md`) in a
single OpenSpec change
(`bulk-import-pre-existing-wip`), and push the
commit(s) to `origin/main`. The capability is the
formal record of which dirty-worktree entries were
adopted, which were deferred, and which were
skipped. Future maintainers can read the absorbed
list from this spec plus the change's
`verification.md` and the updated Phase 6 docs.

## ADDED Requirements

### Requirement: Bulk slice adopts every A + B entry from the Phase 6 matrix

The system SHALL adopt every A + B entry from the
Phase 6 matrix
(`docs/00-project/wip-disposition-matrix.md`) in a
single OpenSpec change
(`bulk-import-pre-existing-wip`). The adopted list
is the A + B entries from the matrix, minus the
duplicate spec (matrix entry #84) which is skipped
per the Phase 6 recommendation.

#### Scenario: A-class deletions are committed

- **WHEN** the dirty worktree contains deletions
  under `openspec/changes/add-community-skill-discovery/`
- **THEN** the bulk-slice commit stages the 7
  deletions and the 11 untracked archive folders
  that correspond to them

#### Scenario: A-class archive folders are committed

- **WHEN** the dirty worktree contains untracked
  `openspec/changes/archive/2026-05-*/` folders
- **THEN** the bulk-slice commit stages every file
  in every archive folder

#### Scenario: B-class modified tracked files are committed

- **WHEN** the dirty worktree contains modified
  tracked files under `openspec/specs/`, `src/`,
  or `tests/`
- **THEN** the bulk-slice commit stages every
  modified tracked file in the B-class list

#### Scenario: B-class untracked files are committed

- **WHEN** the dirty worktree contains untracked
  files under `openspec/specs/`, `src/`, `tests/`,
  or `docs/`
- **THEN** the bulk-slice commit stages every
  untracked file in the B-class list

### Requirement: Duplicate spec is skipped

The system SHALL NOT commit the duplicate
`openspec/specs/skill-lifecycle-recommendation/spec.md`
(matrix entry #84). The file remains untracked. The
Phase 6 matrix recommends "Discard" for this entry;
the bulk slice does not commit the duplicate.

#### Scenario: Duplicate spec is not in the staged set

- **WHEN** the bulk-slice commit is created
- **THEN** the staged set does not include
  `openspec/specs/skill-lifecycle-recommendation/spec.md`

### Requirement: D + E entries are deferred

The system SHALL NOT commit any D-class or E-class
entry in this slice. The D-class entries
(`.claude/**`, `.codex/**`) are deferred to a
future `add-local-tool-gitignore-excludes` change.
The E-class entries (14 files) are deferred for the
user's per-file decision.

#### Scenario: D-class entries are not in the staged set

- **WHEN** the bulk-slice commit is created
- **THEN** the staged set does not include any
  file under `.claude/` or `.codex/`

#### Scenario: E-class entries are not in the staged set

- **WHEN** the bulk-slice commit is created
- **THEN** the staged set does not include
  `AGENT.md`, `docs/intelligent-generation-*.md`,
  `docs/rectification/skill-forge-phase-*-taskbook.md`
  (7 files), `docs/release-notes.md`,
  `docs/skill_forge_next_evolution_plan.md`, or
  `docs/skill_generation_roadmap.md`

### Requirement: Phase 6 docs are updated

The system SHALL update
`docs/00-project/wip-disposition-matrix.md`,
`docs/00-project/change-queue.md`, and
`docs/00-project/dirty-worktree-triage-report.md`
to mark the absorbed entries as done. The updates
land in the same bulk-slice commit.

#### Scenario: Matrix marks absorbed entries

- **WHEN** the bulk-slice commit is created
- **THEN** the updated
  `wip-disposition-matrix.md` has an "Absorbed by"
  annotation per absorbed entry

#### Scenario: Queue marks absorbed future changes

- **WHEN** the bulk-slice commit is created
- **THEN** the updated `change-queue.md` has a
  "Status" or "Absorbed by" annotation per
  absorbed future change

#### Scenario: Report adds a Phase 7 section

- **WHEN** the bulk-slice commit is created
- **THEN** the updated
  `dirty-worktree-triage-report.md` has a
  "Phase 7 Bulk Slice" section that records the
  commit SHA, the deferred D + E entries, and the
  push confirmation

### Requirement: Per-path `git add` discipline

The system SHALL stage every adopted path with
explicit `git add <path>`. The system SHALL NOT
use `git add .`, `git add -A`, or `git add -u`.

#### Scenario: Staged set is verified

- **WHEN** the bulk-slice commit is created
- **THEN** the staged set is verified with
  `git diff --cached --stat` and
  `git diff --cached --name-only` before the
  commit is created

### Requirement: Push after the commit lands

The system SHALL push the bulk-slice commit and the
follow-up docs commit to `origin/main` after both
land locally. The system SHALL NOT push the
pre-existing Phase 0-6 commits (they were committed
before the "push after every future change" rule
was set).

#### Scenario: Push succeeds

- **WHEN** the bulk-slice commit and the follow-up
  docs commit are created locally
- **THEN** `git push origin main` succeeds and
  `origin/main` advances to the follow-up docs
  commit

#### Scenario: Push is verifiable

- **WHEN** the push succeeds
- **THEN** `git log --oneline origin/main -2`
  shows the follow-up docs commit and the
  bulk-slice commit at the top of `origin/main`

## MODIFIED Requirements

None. The pre-existing capabilities in
`openspec/specs/*` are not modified at the OpenSpec
level by this slice. The B-class additions to the
modified specs and the new B-class spec files are
adopted as-is from the dirty worktree; they are not
re-shaped by this slice.

## REMOVED Requirements

### Requirement: (none)

This capability does not remove any existing
requirement.

## RENAMED Requirements

### Requirement: (none)

This capability does not rename any existing
requirement.
