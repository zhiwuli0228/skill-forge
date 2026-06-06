# Design: triage-dirty-worktree-change-queue

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md

## Context

Phases 0-5 introduced a working OpenSpec governance
stack and shipped five governed changes. After Phase 5
the working tree is dirty with:

- 30 modified tracked files
  (`docs/`, `openspec/specs/`, `src/`, `tests/`);
- 8 deletions under
  `openspec/changes/add-community-skill-discovery/`
  (the active folder was archived to
  `openspec/changes/archive/2026-05-28-add-community-skill-discovery/`
  but the deletion was not committed);
- ~70 untracked entries spanning `.claude/`, `.codex/`,
  `AGENT.md`, `docs/`, `openspec/changes/archive/`,
  `openspec/specs/`, `src/`, and `tests/`.

The dirty surface is exclusively user-side WIP plus
locally generated tool files. No code change in
`src/`, `tests/`, `templates/`, `configs/`, or
`scripts/` is in scope for this phase.

The Phase 6 task is documentation-only. The triage
records the disposition of every dirty entry and the
recommended future change queue. The phase must not
delete, reset, restore, or clean the dirty worktree.

## Goals / Non-Goals

### Goals

- Produce a per-entry classification of every dirty
  entry into the A/B/C/D/E categories.
- Produce a recommended change queue of future
  OpenSpec changes in priority order.
- Produce a top-level narrative that ties the matrix
  and the queue together.
- Validate the OpenSpec change under
  `openspec validate --strict --all`.
- Pass the quick governance check
  (`python scripts/governance_check.py --quick`).

### Non-Goals

- (restate from proposal.md) Implement any feature in
  the dirty worktree.
- (restate from proposal.md) Delete, reset, restore, or
  clean the dirty worktree.
- (restate from proposal.md) Modify any pre-existing
  OpenSpec change folder (active or archived).
- (restate from proposal.md) Introduce a `.gitignore`
  rule.
- (restate from proposal.md) Archive the Phase 3/4/5
  changes.
- Re-shape the dirty entries. The triage records the
  recommended disposition; a future governed change
  is the right place to actually move, edit, or delete
  the entries.

## Decisions

### Decision 1: Use the A/B/C/D/E classification scheme

- **Decision**: every dirty entry is classified into
  one of five buckets:
  - **A. Absorbed by prior phases** — the entry is
    already represented in a committed change or in a
    working-tree archive copy of a committed change.
  - **B. Candidate for future governed change** — the
    entry is a new source module, new spec, or new
    test that needs an OpenSpec change to be properly
    tracked.
  - **C. Existing change needs reshape** — the entry
    is a tracked modification to a file that belongs
    to an active change and should be folded into
    that change.
  - **D. Candidate for discard** — the entry is an
    obsolete or local-only artifact (e.g. `.claude/`,
    `.codex/`) that should be ignored rather than
    tracked.
  - **E. Requires user decision** — the entry is
    ambiguous; the disposition depends on the user's
    intent.
- **Rationale**: the five-bucket scheme is small
  enough to fit in a single table and exhaustive
  enough to cover every dirty entry observed in
  Phase 6. It mirrors common change triage rubrics
  (absorb / shape / discard / escalate).
- **Alternatives considered**: a two-bucket scheme
  (commit / discard) is too coarse; an eight-bucket
  scheme is too granular. The five-bucket scheme is
  the sweet spot.

### Decision 2: The disposition matrix is a single
markdown table

- **Decision**: the matrix
  (`docs/00-project/wip-disposition-matrix.md`) is a
  single markdown table with columns
  `Path | Status | Class | Reason | Recommended action`.
- **Rationale**: a single table is greppable, easy to
  extend, and easy to diff. The five-bucket classification
  fits naturally as a single column.
- **Alternatives considered**: one table per bucket
  is harder to scan; one file per entry is overkill.
  A single table is the simplest readable form.

### Decision 3: The change queue is a single markdown
list of future OpenSpec changes

- **Decision**: the change queue
  (`docs/00-project/change-queue.md`) is a numbered
  list of future OpenSpec change ids, each with a
  one-line description, the blocking dependency, and
  the expected effort.
- **Rationale**: a numbered list gives a natural
  priority order and a natural "next change" pointer.
  A list is also easy to reorder.
- **Alternatives considered**: a Gantt-style chart is
  overkill for a documentation-only phase. A list
  is the simplest readable form.

### Decision 4: The top-level report is a narrative
summary, not a duplicate of the matrix or the queue

- **Decision**: the top-level report
  (`docs/00-project/dirty-worktree-triage-report.md`)
  is a narrative that ties the matrix and the queue
  together, lists the verification commands, and
  records the Phase 6 commit SHA. It does not repeat
  the table rows.
- **Rationale**: the matrix and the queue are
  authoritative for the per-entry data; the report
  is the human-readable surface. Duplicating data
  invites drift.
- **Alternatives considered**: a single consolidated
  doc is simpler but harder to navigate. The three
  files (matrix, queue, report) mirror the Phase 5
  pattern (one OpenSpec change + one verification
  report).

### Decision 5: Phase 6 ships only the four new
files; the dirty worktree is left untouched

- **Decision**: the Phase 6 commit includes only
  the OpenSpec change folder and the three new doc
  files. No source code, test, template, config,
  script, or pre-existing OpenSpec change is
  committed or modified.
- **Rationale**: the strict-scope allowed-path list
  in the Phase 6 task is the authoritative scope.
  Touching any other file is a scope violation.
- **Alternatives considered**: folding the
  disposition matrix's `D` entries (`.claude/`,
  `.codex/`) into a `.gitignore` change in the same
  commit would expand the scope and violate the
  dirty worktree rule.

## Data Contracts

No schema changes. The phase is documentation-only.

### `wip-disposition-matrix.md` (new file)

```yaml
# Schema (informal)
columns:
  - path: relative path from repo root
  - status: "M" (modified) | "D" (deleted) | "A" (untracked, new file)
  - class: "A" | "B" | "C" | "D" | "E"
  - reason: one-line reason for the classification
  - recommended_action: the next step the user or a
    future change should take
```

### `change-queue.md` (new file)

```yaml
# Schema (informal)
columns:
  - rank: integer priority (1 = highest)
  - change_id: kebab-case OpenSpec change id
  - description: one-line description
  - depends_on: change_id or "none"
  - effort: "small" | "medium" | "large"
  - source_buckets: list of A/B/C/D/E entries that
    this change will absorb
```

### `dirty-worktree-triage-report.md` (new file)

A free-form narrative. Contains the verification
command results and the Phase 6 commit SHA.

## Module Boundaries

### Added

- `openspec/changes/triage-dirty-worktree-change-queue/.openspec.yaml`:
  the OpenSpec change skeleton header.
- `openspec/changes/triage-dirty-worktree-change-queue/brainstorm.md`:
  the brainstorm artifact.
- `openspec/changes/triage-dirty-worktree-change-queue/proposal.md`:
  the proposal artifact.
- `openspec/changes/triage-dirty-worktree-change-queue/design.md`:
  this file.
- `openspec/changes/triage-dirty-worktree-change-queue/review.md`:
  the review artifact (verdict `approve`).
- `openspec/changes/triage-dirty-worktree-change-queue/plan.md`:
  the executable plan.
- `openspec/changes/triage-dirty-worktree-change-queue/tasks.md`:
  the checkbox-tracked task list.
- `openspec/changes/triage-dirty-worktree-change-queue/verification.md`:
  the OpenSpec-level evidence record.
- `openspec/changes/triage-dirty-worktree-change-queue/specs/dirty-worktree-change-queue/spec.md`:
  the new capability spec.
- `docs/00-project/dirty-worktree-triage-report.md`:
  the top-level narrative.
- `docs/00-project/wip-disposition-matrix.md`:
  the per-entry A/B/C/D/E table.
- `docs/00-project/change-queue.md`:
  the recommended future change queue.

### Modified

None. The strict-scope allowed-path list restricts
the phase to creating new files only. No pre-existing
file is modified by this phase.

### Untouched

- Every file under `src/`, `tests/`, `templates/`,
  `configs/`, `scripts/`, `pyproject.toml`, `uv.lock`.
- Every pre-existing `openspec/changes/**` folder
  (active or archived).
- `openspec/specs/**` (the pre-existing specs are
  not modified by this phase; the untracked spec
  files are recorded in the matrix as `B`).
- `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`, `AGENTS.md`, `CODEX.md`,
  `CLAUDE.md`, `OPENCODE.md`, `SUPERPOWERS.md`,
  `README.md`, `README.zh-CN.md`.
- `openspec/config.yaml`, `openspec/schemas/**`.

## Compatibility Impact

- Claude Code: no effect.
- Codex: no effect.
- opencode: no effect.
- Generated Skill packages: no effect.

## Offline and Deterministic Mode

- Network unavailable: the triage is documentation-only
  and runs entirely offline.
- LLM disabled: the triage is documentation-only and
  does not invoke the LLM.
- LLM enabled but config missing: the triage is
  documentation-only and does not invoke the LLM.

## Security and Filesystem

- Reads:
  - `git status --short` to enumerate the dirty
    surface.
  - `git diff --name-only` and
    `git ls-files --others --exclude-standard` for
    the per-file classification.
  - `git diff --stat` and
    `git log --oneline -10` for the verification
    record.
- Writes: the 12 new files in the strict-scope
  allowed-path list. No pre-existing file is
  modified.
- Environment variables: none.

## Risks / Trade-offs

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
- [The `.claude/` and `.codex/` directories are
  recorded as `D` but a follow-up change is needed
  to add them to `.gitignore`] -> Mitigation: the
  matrix explicitly lists the follow-up change in
  the change queue as
  `add-local-tool-gitignore-excludes`.

## Migration Plan

### Deploy

1. Stage the 12 new files explicitly with
   `git add <path>` (no `git add .` or `git add -A`).
2. Commit with the suggested message
   `docs: triage dirty worktree change queue`.
3. Optionally, create a follow-up docs commit
   recording the SHA in the verification.md and the
   top-level report (mirroring the Phase 3-5 pattern).

### Rollback

1. Delete the OpenSpec change folder
   `openspec/changes/triage-dirty-worktree-change-queue/`.
2. Delete the three new doc files
   `docs/00-project/dirty-worktree-triage-report.md`,
   `docs/00-project/wip-disposition-matrix.md`, and
   `docs/00-project/change-queue.md`.
3. The dirty worktree is unaffected. No code, test,
   template, config, or pre-existing OpenSpec change
   is touched, so rollback is a pure file delete.

## Open Questions

- [non-blocking] Should the disposition matrix include
  the `.claude/` and `.codex/` local tool directories
  as `D` (candidate for discard via `.gitignore`), or
  should they be excluded from the matrix because they
  are not "code or spec WIP"? Recommend: include them
  with a clear `D` label and a follow-up `.gitignore`
  change.
- [non-blocking] Should the Phase 6 commit include only
  the 12 new files, or should it also include a
  follow-up docs commit recording the SHA, mirroring
  the Phase 3-5 pattern? Recommend: include a follow-up
  docs commit if the user wants the SHA traceability.
