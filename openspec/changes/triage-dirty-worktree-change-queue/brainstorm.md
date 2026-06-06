# Brainstorm: triage-dirty-worktree-change-queue

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 6 (dirty worktree triage)
> Date: 2026-06-06
>
> Brainstorm is the FIRST artifact for a non-trivial change.
> It is required because the change introduces a new
> governance artifact type (the WIP disposition matrix and
> the change queue ledger) and reshapes how future changes
> are sequenced.

## Problem

Phases 0-5 introduced a working OpenSpec governance stack
(brainstorm → proposal → spec → design → review → plan →
tasks → verification) and shipped five governed changes.
After Phase 5, the working tree still carries a large
pre-existing dirty worktree that mixes:

- changes that were already archived but whose active
  folder was never deleted on disk;
- new modules, specs, and tests for capabilities that
  have not yet been packaged as OpenSpec changes;
- local tool directories (`.claude/`, `.codex/`) that
  should be ignored rather than tracked;
- design notes and taskbooks in `docs/` whose
  disposition (commit / archive / discard) is not yet
  decided.

The dirty worktree blocks the next agent from starting
a clean governed change, because the uncommitted surface
is large enough that a future change cannot easily
separate "its own work" from "user WIP". We need a
triage artifact (this change) that classifies every
dirty entry, lists the recommended future changes, and
records which entries require a human decision. The
triage change itself is documentation-only; it must not
implement features or delete user work.

## Context

- Current state: the working tree is dirty with 30
  modified tracked files, 8 deletions under
  `openspec/changes/add-community-skill-discovery/`, and
  ~70 untracked entries spanning `.claude/`, `.codex/`,
  `docs/`, `openspec/changes/archive/`,
  `openspec/specs/`, `src/`, and `tests/`. Phases 0-5 are
  fully committed. The dirty surface is exclusively
  user-side WIP plus locally generated tool files.
- Constraints: this phase is a documentation-only
  governance slice. The strict-scope allowed-path list
  restricts creation to the OpenSpec change folder and
  three `docs/00-project/` files. The phase must not
  touch `src/`, `tests/`, `templates/`, `configs/`,
  `scripts/`, `pyproject.toml`, `uv.lock`, the existing
  governance doc folders, the schema folders, or any
  pre-existing OpenSpec change folder. The phase must
  not reset, delete, restore, or clean the dirty
  worktree.
- Stakeholders: the Skill Forge maintainer who wants
  the dirty worktree triaged; future change authors who
  need a clean baseline; the OpenSpec change queue
  tracker that needs a recommended sequencing.

## Options

### Option A: Single triage change with three doc artifacts (recommended)

- **Changes**: create
  `openspec/changes/triage-dirty-worktree-change-queue/`
  with eight governance artifacts plus a new spec
  capability; create `docs/00-project/wip-disposition-matrix.md`
  (per-entry A/B/C/D/E classification), `docs/00-project/change-queue.md`
  (the recommended sequence of future governed
  changes), and `docs/00-project/dirty-worktree-triage-report.md`
  (the top-level narrative). The OpenSpec change folder
  is the formal record; the three doc files are the
  human-readable summary.
- **Does not change**: every dirty entry stays on disk.
  No code is touched. No existing OpenSpec change is
  modified. No deletion, reset, or clean is performed.
- **Top risk**: the three doc files and the OpenSpec
  artifacts may drift if a future agent updates one
  and not the others. Mitigation: the OpenSpec
  verification.md is the single source of truth, and
  the doc files explicitly defer to it.
- **Effort**: small (one phase, documentation only).

### Option B: Triage change with a single consolidated doc

- **Changes**: same OpenSpec change folder, but the
  human-readable summary is one file
  `docs/00-project/dirty-worktree-triage-report.md` that
  embeds the disposition matrix and the change queue
  inline.
- **Does not change**: same as Option A.
- **Top risk**: a single consolidated doc becomes hard
  to navigate once the queue grows past ~5 changes.
  The two separate doc files (matrix, queue) are
  future-proof.
- **Effort**: small (slightly smaller than Option A).

### Option C: Triage change without OpenSpec governance

- **Changes**: write only
  `docs/00-project/dirty-worktree-triage-report.md`.
  Skip the OpenSpec change folder entirely.
- **Does not change**: same as Option A.
- **Top risk**: the triage is not itself a governed
  change, so a future maintainer cannot trace the
  triage back to a reviewed proposal. This violates
  the Phase 0 governance rule that any non-trivial
  change must live under `openspec/changes/`.
- **Effort**: smallest.

## Assumptions

- [verified] The OpenSpec governance schema
  `skill-forge-governance` (introduced in Phase 1) is
  the active schema and requires eight artifacts per
  change.
- [verified] Phases 0-5 are fully committed; the dirty
  surface is exclusively user-side WIP plus locally
  generated tool files.
- [verified] The strict-scope allowed-path list in the
  Phase 6 task is the authoritative scope for this
  phase.
- [unverified] The user wants a per-entry A/B/C/D/E
  classification in the disposition matrix. The
  classification scheme is recommended by the
  brainstorm; the user may simplify it.
- [unverified] The user wants the future change queue
  sequenced in a particular order. The brainstorm
  recommends a natural ordering by dependency and
  risk; the user may reorder.

## Open Questions

- [non-blocking] Should the disposition matrix include
  the `.claude/` and `.codex/` local tool directories
  as `D` (candidate for discard via `.gitignore`), or
  should they be excluded from the matrix because they
  are not "code or spec WIP"? Recommend: include them
  with a clear `D` label and a follow-up `.gitignore`
  change.
- [non-blocking] Should the Phase 6 commit include only
  the four new files (the OpenSpec change folder plus
  the three doc files), or should it also include a
  follow-up docs commit recording the SHA, mirroring
  the Phase 3-5 pattern? Recommend: include a follow-up
  docs commit if the user wants the SHA traceability.
- [blocking] None. The classification scheme, the
  change queue ordering, and the commit style are all
  judgment calls the implementer can make within the
  strict-scope allowed-path list.

## Recommendation

- Recommended: **Option A**.
- Reason: the OpenSpec change folder provides the
  reviewable record, the three doc files provide the
  human-readable surface, and the matrix + queue split
  is future-proof. Option B is acceptable but less
  navigable; Option C violates the Phase 0 governance
  rule.
