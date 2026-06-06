# Dirty Worktree Change Queue Specification

> Status: draft
> Schema: skill-forge-governance
> Capability: `dirty-worktree-change-queue`
> File: `specs/dirty-worktree-change-queue/spec.md`
>
> This spec describes the governance capability that
> records the A/B/C/D/E classification scheme and the
> change queue ledger. The capability is
> documentation-only: it does not implement any feature
> and does not modify the dirty worktree.

## Purpose

Centralize the A/B/C/D/E classification scheme and the
recommended change queue ledger in a single governance
capability, so that future change authors can read the
disposition of every dirty entry and the recommended
sequencing of future changes from one spec plus two
companion doc files
(`docs/00-project/wip-disposition-matrix.md` and
`docs/00-project/change-queue.md`).

## ADDED Requirements

### Requirement: Disposition matrix records every dirty entry

The system SHALL record the disposition of every dirty
entry in the working tree at the time the triage is
taken, in
`docs/00-project/wip-disposition-matrix.md`, classified
into exactly one of five buckets:
`A` (absorbed by prior phases), `B` (candidate for
future governed change), `C` (existing change needs
reshape), `D` (candidate for discard), or
`E` (requires user decision).

#### Scenario: A modified source file is recorded as B

- **WHEN** the dirty worktree contains a modified
  source file under `src/skill_forge/`
- **THEN** the matrix records the file with
  `Status: M` and `Class: B` (or `C` if the
  modification belongs to an active change)

#### Scenario: A deleted active change is recorded as A

- **WHEN** the dirty worktree contains deletions
  under an active `openspec/changes/<change-id>/`
  folder that has a corresponding copy under
  `openspec/changes/archive/<date>-<change-id>/`
- **THEN** the matrix records every deleted file with
  `Status: D` and `Class: A` (the change is already
  archived; the working-tree deletion is the result of
  an archive operation that was not yet committed)

#### Scenario: A local tool directory is recorded as D

- **WHEN** the dirty worktree contains an untracked
  local tool directory (e.g. `.claude/`, `.codex/`)
- **THEN** the matrix records the directory with
  `Status: A` (untracked, new file) and `Class: D`
  (candidate for discard via a follow-up
  `.gitignore` change)

### Requirement: Change queue lists future OpenSpec changes in priority order

The system SHALL record the recommended future
OpenSpec change queue in
`docs/00-project/change-queue.md`, ordered by
priority, with a one-line description, the blocking
dependency, the expected effort, and the source
buckets (A/B/C/D/E entries) that the change will
absorb.

#### Scenario: A change that depends on a prior change is recorded

- **WHEN** a future change `add-foo` depends on a
  prior change `add-bar`
- **THEN** the queue records `add-foo` with
  `Depends on: add-bar` and a strictly higher rank
  number than `add-bar`

#### Scenario: A change that absorbs B-class entries is recorded

- **WHEN** a future change `add-foo` will absorb a set
  of `B`-class entries from the disposition matrix
- **THEN** the queue records `add-foo` with
  `Source buckets: B (file1, file2, ...)` listing
  every B-class entry that the change will absorb

### Requirement: Top-level report ties matrix and queue together

The system SHALL record the top-level narrative in
`docs/00-project/dirty-worktree-triage-report.md`,
which summarizes the matrix and the queue, lists the
verification commands, and records the Phase 6
commit SHA.

#### Scenario: Report records the verification commands

- **WHEN** a reader opens the top-level report
- **THEN** the report contains a section listing the
  exact verification commands run, the exit codes,
  and the observed outputs

#### Scenario: Report records the Phase 6 commit SHA

- **WHEN** the Phase 6 commit is created
- **THEN** the report contains a `## Commit SHA`
  section recording the short SHA, the full SHA, the
  commit message, and the explicit
  `git add <path>` discipline used

### Requirement: Triage is documentation-only

The system SHALL NOT implement any feature, delete
any dirty entry, reset the working tree, restore any
file, or clean the dirty worktree as part of the
triage. The triage records the recommended
disposition; the actual change is the work of a
future OpenSpec change.

#### Scenario: No source file is modified by the triage

- **WHEN** the Phase 6 commit is created
- **THEN** the commit's changed file list is exactly
  the strict-scope allowed-path list: the OpenSpec
  change folder plus the three new doc files

#### Scenario: No pre-existing OpenSpec change is modified by the triage

- **WHEN** the Phase 6 commit is created
- **THEN** the commit's changed file list does not
  include any file under
  `openspec/changes/<existing-change-id>/` (active or
  archived)

## MODIFIED Requirements

None. The pre-existing capabilities in
`openspec/specs/*` are out of scope for this slice.
The dirty entries that look like modified capabilities
(see the WIP disposition matrix) will be re-evaluated
by the future change that adopts them.

## REMOVED Requirements

### Requirement: (none)

This capability does not remove any existing
requirement.

## RENAMED Requirements

### Requirement: (none)

This capability does not rename any existing
requirement.
