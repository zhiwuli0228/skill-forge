# Proposal: bulk-import-pre-existing-wip

> Status: draft
> Schema: skill-forge-governance
> Author: Skill Forge Phase 7 (bulk pre-existing WIP import)
> Date: 2026-06-06

## Why

After Phase 6 the working tree still carries a
substantial pre-existing dirty worktree. The Phase 6
triage
(`docs/00-project/wip-disposition-matrix.md`)
classified 112 entries into A (absorbed), B (candidate
for future governed change), D (candidate for discard),
and E (requires user decision). The Phase 6
recommendation was to ship each B-class entry as its
own OpenSpec change, the D-class entries as a separate
`.gitignore` change, and the E-class entries for the
user's per-file decision. The user has now decided to
commit the A + B entries in a single bulk-slice
OpenSpec change and to defer D + E. This phase
executes the bulk slice with the same 8-artifact
governance pattern used in Phases 0-6, and pushes the
commit(s) to `origin/main` per the user's "push after
every future change" rule.

## What Changes

- New governance capability
  `pre-existing-wip-bulk-import` that records the
  bulk-slice governance and the absorbed-entry list.
- New OpenSpec change folder
  `openspec/changes/bulk-import-pre-existing-wip/`
  with the standard eight governance artifacts plus
  a new spec file.
- New top-level doc
  `docs/00-project/bulk-import-verification-report.md`
  that records the verification command results and
  the Phase 7 commit SHA.
- Update `docs/00-project/wip-disposition-matrix.md`
  to mark the absorbed entries as "absorbed by
  `bulk-import-pre-existing-wip`".
- Update `docs/00-project/change-queue.md` to mark
  the absorbed future changes as done.
- Update `docs/00-project/dirty-worktree-triage-report.md`
  to add a section describing the Phase 7 bulk slice
  and the deferred D + E entries.
- **A-class entries (18 total)**:
  - Commit the 7 deletions under
    `openspec/changes/add-community-skill-discovery/`.
  - Commit the 11 untracked
    `openspec/changes/archive/2026-05-*/` folders.
- **B-class entries (42 total)**:
  - Commit the 21 modified tracked files
    (7 `openspec/specs/*/spec.md` files, 9
    `src/skill_forge/**/*.py` files, 5
    `tests/test_*.py` files).
  - Commit the 1 untracked doc
    `docs/skill_lifecycle_governance_plan.md`.
  - Commit the 6 untracked spec files in
    `openspec/specs/*/spec.md`.
  - Commit the 10 untracked source modules under
    `src/skill_forge/{adoption,experience,lifecycle,models,retrieval}/`.
  - Commit the 4 untracked test files under
    `tests/test_*.py`.
- **D-class entries (24 total)**: DEFERRED to a
  future `add-local-tool-gitignore-excludes` change.
- **E-class entries (14 total)**: DEFERRED for the
  user's per-file decision.
- **Duplicate spec**: SKIPPED per the Phase 6 matrix
  recommendation (entry #84,
  `openspec/specs/skill-lifecycle-recommendation/spec.md`
  is a duplicate of the Phase 3 spec and should be
  discarded, not committed).
- **Push**: push the Phase 7 commit(s) to
  `origin/main` per the user's "push after every
  future change" rule. The pre-existing Phase 0-6
  commits are NOT pushed in this turn (they were
  committed before the push rule was set).

## Capabilities

### New Capabilities

- `pre-existing-wip-bulk-import`: a governance
  capability that records the bulk-slice governance
  and the absorbed-entry list, so that future
  maintainers can trace which dirty-worktree entries
  were absorbed by this slice and which were deferred.

### Modified Capabilities

None. The pre-existing capabilities in
`openspec/specs/*` are not modified by this slice at
the OpenSpec level. The B-class additions to the
modified specs and the new B-class spec files are
adopted as-is from the dirty worktree; they are not
re-shaped by this slice. The 7 modified
`openspec/specs/*/spec.md` files (entries #10-#16)
gain their modifications in this commit, but the
spec text is preserved verbatim from the dirty
worktree.

### Removed Capabilities

None. The pre-existing capabilities are preserved.
No capability is retired by this slice.

## Impact

- Code: 9 `src/skill_forge/**/*.py` files modified
  (additions from the dirty worktree); 10
  `src/skill_forge/**` source modules added (new
  modules: `adoption`, `experience`, `lifecycle`
  parts, `models/experience.py`,
  `retrieval/generation.py`).
- CLI: the dirty-worktree modifications to
  `src/skill_forge/cli.py` are preserved as-is. The
  CLI smoke test must pass after the slice lands.
- Tests: 5 `tests/test_*.py` files modified
  (additions from the dirty worktree); 4
  `tests/test_*.py` files added (`test_experience.py`,
  `test_lifecycle.py`, `test_promotion.py`,
  `test_skill_adoption.py`).
- Schemas: 7 `openspec/specs/*/spec.md` files
  modified; 6 new `openspec/specs/*/spec.md` files
  added.
- Workspaces: existing Skill Forge workspaces are
  unaffected. The dirty worktree is absorbed; the
  remaining untracked entries are the deferred D + E
  classes and the skipped duplicate spec.
- OpenSpec governance: 11 new
  `openspec/changes/archive/2026-05-*/` folders are
  committed (these are the user's pre-existing
  archive copies of past changes); 7 deletions under
  `openspec/changes/add-community-skill-discovery/`
  are committed.

## Non-Goals

- This change does not re-shape the B-class
  additions. The dirty-worktree content is adopted
  verbatim.
- This change does not modify the `.gitignore`. The
  D-class entries (`.claude/**`, `.codex/**`) are
  deferred to a future
  `add-local-tool-gitignore-excludes` change.
- This change does not act on any E-class entry.
  The 14 E-class entries (AGENT.md,
  docs/intelligent-generation-*.md, docs/rectification/*.md,
  docs/release-notes.md, the 2 modified WIP docs)
  are deferred for the user's per-file decision.
- This change does not push the pre-existing
  Phase 0-6 commits. Only the Phase 7 commit(s) are
  pushed.
- This change does not modify any pre-existing
  OpenSpec change folder (Phase 0-6) or any
  governance doc outside the strict-scope list.
- This change does not modify `pyproject.toml`,
  `uv.lock`, `templates/**`, `configs/**`,
  `scripts/**`, `README*`, `AGENTS*`/`CODEX*`/`CLAUDE*`/
  `OPENCODE*`/`SUPERPOWERS*`, `docs/03-openspec/**`,
  `docs/04-superpowers/**`, `.superpowers/**`,
  `openspec/config.yaml`, or `openspec/schemas/**`.

## Risks

- [The bulk slice is large and a per-path `git add`
  typo could include an unintended path] ->
  Mitigation: the strict-scope allowed-path list in
  the plan enumerates every path, and the staging
  step verifies the staged set with
  `git diff --cached --stat` before committing.
- [The B-class additions are adopted verbatim from
  the dirty worktree and may not have been reviewed
  for quality] -> Mitigation: the bulk slice is a
  one-time cleanup; a future governed change can
  re-shape any specific subset if needed.
- [The push to `origin/main` is irreversible; if a
  wrong file lands in the commit, the only rollback
  is a force-push that rewrites shared history] ->
  Mitigation: the commit is staged with explicit
  `git add <path>` for every path; the staged set is
  verified with `git diff --cached --stat` and
  `git diff --cached --name-only` before committing;
  the verification report records the exact staged
  set. The user has authorized the push.
- [The Phase 6 docs may drift from the actual state
  if the matrix counts are off] -> Mitigation: the
  matrix counts in §8 are slightly off (the matrix
  has 56 B but the per-entry table has 42 B); the
  verification report records the corrected count
  (60 = 18 A + 42 B) and the disposition.

## Rollback

1. The local commit can be rolled back with
   `git reset --soft HEAD~1` (or `--mixed`) to
   preserve the working tree.
2. The remote push can be rolled back with
   `git push --force-with-lease origin main` after
   the local reset, but this rewrites shared
   history and is a destructive action that
   requires explicit user confirmation.
3. The skipped duplicate spec
   (`openspec/specs/skill-lifecycle-recommendation/spec.md`)
   can be deleted from the working tree with
   `rm` (the user should decide whether to discard
   it; the Phase 6 matrix recommends discard).
4. The deferred D + E entries are unaffected by
   the rollback (they were not committed in this
   slice).

## Consistency With Brainstorm

- Brainstorm file: `brainstorm.md`
- Recommended option: **Option A** (bulk OpenSpec
  change with explicit per-path `git add`).
- Deviations and reasons: none. The proposal follows
  the brainstorm recommendation. The two non-blocking
  open questions (one commit vs. two; Phase 6 doc
  updates in the same commit) are resolved as
  recommended.
