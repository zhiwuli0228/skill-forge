# Brainstorm: bulk-import-pre-existing-wip

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 7 (bulk pre-existing WIP import)
> Date: 2026-06-06
>
> Brainstorm is the FIRST artifact for a non-trivial
> change. It is required because the change adopts a
> broad set of files from the dirty worktree and
> departs from the strict-scope discipline used in
> Phases 0-6.

## Problem

After Phase 6 the working tree still carries a
substantial pre-existing dirty worktree. The Phase 6
triage
(`docs/00-project/wip-disposition-matrix.md`) classified
112 entries into 18 A (absorbed), 56 B (candidate for
future governed change), 0 C, 24 D (candidate for
discard), and 14 E (requires user decision). The
Phase 6 recommendation was to ship each B-class entry
as its own OpenSpec change, the D-class entries as a
separate `.gitignore` change, and the E-class entries
for the user's per-file decision. That recommendation
preserved the strict-scope discipline but created a
backlog of 12+ future changes. The user has now
decided to commit the A + B entries in a single
bulk-slice OpenSpec change and to defer D + E. The
phase must execute the bulk slice without losing
governance: the slice must have its own 8-artifact
folder, its own spec, and its own verification record.
The phase must also update the Phase 6 docs to mark
the absorbed entries as done.

## Context

- Current state: the working tree is dirty with
  30 modified tracked files, 8 deletions under
  `openspec/changes/add-community-skill-discovery/`,
  and ~70 untracked entries. The Phase 6 governance
  has been shipped locally (commits 351cc7e and
  fa396c5) and the user has now decided to absorb the
  A + B entries in this phase. The remote is at
  `git@github.com:zhiwuli0228/skill-forge.git` on
  `main`; no Phase 0-6 commit has been pushed.
- Constraints: the phase is a bulk-import slice. It
  must have its own 8-artifact OpenSpec change folder
  with the strict-scope allowed-path list explicitly
  listing every A + B entry it adopts. It must not
  touch any D-class entry, any E-class entry, any
  pre-existing Phase 3-6 change, any governance doc
  outside the strict-scope list, or any runtime config
  (`pyproject.toml`, `uv.lock`, `templates/**`,
  `configs/**`, `scripts/**`, `.gitignore`). The
  phase must skip the duplicate
  `openspec/specs/skill-lifecycle-recommendation/spec.md`
  per the Phase 6 matrix recommendation (it is a
  duplicate of the Phase 3 spec and should be
  discarded, not committed). The phase must use
  explicit `git add <path>` for each adopted path; no
  `git add .` or `git add -A`. The phase must push to
  `origin/main` after the commit lands.
- Stakeholders: the user (who wants the dirty
  worktree absorbed and pushed); future change
  authors (who need a clean baseline); the Phase 8+
  maintainer (who will address the deferred D + E
  entries).

## Options

### Option A: Bulk OpenSpec change with explicit per-path
git add (recommended)

- **Changes**: create
  `openspec/changes/bulk-import-pre-existing-wip/`
  with the standard eight governance artifacts plus
  a new spec; create a top-level
  `docs/00-project/bulk-import-verification-report.md`;
  update the Phase 6 docs
  (`wip-disposition-matrix.md`, `change-queue.md`,
  `dirty-worktree-triage-report.md`) to mark the
  absorbed entries as done. Stage every A + B entry
  with explicit `git add <path>`. Commit with the
  message
  `docs: bulk import pre-existing wip`. Push to
  `origin/main` after the commit lands. A follow-up
  docs commit records the SHA in the verification
  report and pushes it.
- **Does not change**: every D-class entry (deferred
  to a future `.gitignore` change). Every E-class
  entry (deferred for user decision). Every
  pre-existing Phase 3-6 change. Every governance doc
  outside the strict-scope list. Every runtime config
  (`pyproject.toml`, `uv.lock`, `templates/**`,
  `configs/**`, `scripts/**`, `.gitignore`).
- **Top risk**: the per-path `git add` list is long
  (~70+ paths) and a typo could either include an
  unintended path or skip an intended one.
  Mitigation: the strict-scope allowed-path list in
  the plan enumerates every path, and the staging
  step verifies the staged set with
  `git diff --cached --stat` before committing.
- **Effort**: small (mechanical, but with a long
  per-path list).

### Option B: Bulk commit with `git add -A`

- **Changes**: same as Option A but uses
  `git add -A` to stage the entire working tree.
- **Does not change**: same as Option A.
- **Top risk**: `git add -A` would also stage the
  D-class entries, the E-class entries, and any
  pre-existing WIP that the strict-scope list
  excludes. The user's dirty-worktree rule explicitly
  forbids `git add .` or `git add -A`. Mitigation:
  none — the rule is a hard constraint.
- **Effort**: smallest.

### Option C: Per-capability bulk commits

- **Changes**: split the bulk slice into N
  per-capability commits (e.g., one for adoption,
  one for experience, one for lifecycle promotion,
  one for content quality, one for retrieval
  augmentation, one for LLM field generation, one
  for CLI/storage extensions, one for the
  governance plan, one for the archive folders).
  Each commit has its own OpenSpec change folder.
- **Does not change**: same as Option A.
- **Top risk**: N is roughly 8-10; the user said
  "one bulk slice" so this option violates the
  user's intent.
- **Effort**: medium (more governance artifacts).

## Assumptions

- [verified] The remote is
  `git@github.com:zhiwuli0228/skill-forge.git` and
  the local branch is `main`.
- [verified] The local branch has 11 un-pushed
  commits (Phases 0-6). The user wants the Phase 7
  commit(s) pushed but has not asked to push the
  earlier phases.
- [verified] The Phase 6 matrix classifies 18 entries
  as A, 56 as B (the matrix has a slight count
  error — the actual A + B count is 18 + 42 = 60 —
  but the per-entry table is correct).
- [verified] The Phase 6 matrix recommends
  "Discard" for
  `openspec/specs/skill-lifecycle-recommendation/spec.md`
  (entry #84). The bulk slice must skip this file.
- [unverified] The user wants a follow-up docs commit
  recording the SHA, mirroring the Phase 3-6 pattern.
  Recommend: yes, follow the same pattern.
- [unverified] The user wants the Phase 6 docs
  updated to mark the absorbed entries as done.
  Recommend: yes, to keep the docs consistent.

## Open Questions

- [non-blocking] Should the bulk-slice commit be
  one commit or two? Recommend: one commit
  (`docs: bulk import pre-existing wip`) plus a
  follow-up docs commit
  (`docs: record Phase 7 commit SHA in verification
  report`).
- [non-blocking] Should the Phase 6 docs be updated
  in the same commit or in a separate commit?
  Recommend: in the same commit, so the docs and the
  absorbed entries land together.
- [non-blocking] Should the Phase 6 strict-scope
  rule be relaxed for this slice? Recommend: yes.
  The strict-scope rule was for documentation-only
  phases; this slice is a code-import phase with
  broader scope. The plan explicitly lists the
  broader allowed-path set.
- [blocking] None. The slice can proceed with the
  recommended options.

## Recommendation

- Recommended: **Option A**.
- Reason: the user explicitly chose "one bulk slice
  with defer D/E" and "push after every future
  change". Option A follows the user's direction,
  preserves the OpenSpec governance pattern, and uses
  the explicit per-path `git add` discipline to
  prevent scope drift. Option B violates the
  dirty-worktree rule. Option C violates the
  "one bulk slice" constraint.
