# Design: bulk-import-pre-existing-wip

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md

## Context

After Phase 6 the working tree still carries a
substantial pre-existing dirty worktree. The Phase 6
triage
(`docs/00-project/wip-disposition-matrix.md`)
classified 112 entries into 18 A (absorbed by prior
phases), 42 B (candidate for future governed change —
the matrix says 56 but the per-entry table sums to
42; the count error is documented in the
verification report), 0 C, 24 D (candidate for
discard), and 14 E (requires user decision). The
Phase 6 recommendation was to ship each B-class entry
as its own OpenSpec change, the D-class entries as a
separate `.gitignore` change, and the E-class entries
for the user's per-file decision. The user has now
decided to commit the A + B entries in a single
bulk-slice OpenSpec change and to defer D + E. This
phase executes the bulk slice with the same
8-artifact governance pattern used in Phases 0-6 and
pushes the commit(s) to `origin/main` per the user's
"push after every future change" rule.

## Goals / Non-Goals

### Goals

- Adopt every A + B entry from the Phase 6 matrix
  in a single bulk-slice OpenSpec change.
- Skip the duplicate
  `openspec/specs/skill-lifecycle-recommendation/spec.md`
  per the Phase 6 matrix recommendation (it is a
  duplicate of the Phase 3 spec).
- Update the Phase 6 docs to mark the absorbed
  entries as done and to add a "Deferred entries"
  section for the D + E classes.
- Push the Phase 7 commit(s) to `origin/main` per
  the user's "push after every future change" rule.
- Validate the OpenSpec change under
  `openspec validate --strict --all`.
- Pass the quick governance check
  (`python scripts/governance_check.py --quick`).
- Pass the full governance check
  (`python scripts/governance_check.py`).
- Pass the test suite
  (`uv run pytest`) — the dirty worktree additions
  may break tests; the slice must not regress the
  310-test baseline.

### Non-Goals

- (restate from proposal.md) Re-shape the B-class
  additions; the dirty-worktree content is adopted
  verbatim.
- (restate from proposal.md) Modify `.gitignore`; the
  D-class entries are deferred.
- (restate from proposal.md) Act on any E-class
  entry; the 14 E-class entries are deferred for
  the user's per-file decision.
- (restate from proposal.md) Push the pre-existing
  Phase 0-6 commits.
- (restate from proposal.md) Modify any pre-existing
  OpenSpec change folder (Phase 0-6) or any
  governance doc outside the strict-scope list.
- (restate from proposal.md) Modify `pyproject.toml`,
  `uv.lock`, `templates/**`, `configs/**`,
  `scripts/**`, `README*`, `AGENTS*`/`CODEX*`/`CLAUDE*`/
  `OPENCODE*`/`SUPERPOWERS*`, `docs/03-openspec/**`,
  `docs/04-superpowers/**`, `.superpowers/**`,
  `openspec/config.yaml`, or `openspec/schemas/**`.

## Decisions

### Decision 1: One bulk-slice OpenSpec change with
explicit per-path `git add`

- **Decision**: create
  `openspec/changes/bulk-import-pre-existing-wip/`
  with the standard eight governance artifacts plus
  a new spec file. Stage every A + B entry with
  explicit `git add <path>`. Commit with the message
  `docs: bulk import pre-existing wip`. Push to
  `origin/main` after the commit lands. A follow-up
  docs commit records the SHA in the verification
  report and pushes it.
- **Rationale**: the user explicitly chose "one bulk
  slice with defer D/E" and "push after every future
  change". Option A follows the user's direction and
  preserves the OpenSpec governance pattern.
- **Alternatives considered**: Option B
  (`git add -A`) violates the dirty-worktree rule.
  Option C (per-capability commits) violates the
  "one bulk slice" constraint.

### Decision 2: Skip the duplicate spec

- **Decision**: skip
  `openspec/specs/skill-lifecycle-recommendation/spec.md`
  (matrix entry #84) from the bulk slice. The file
  remains untracked. The Phase 6 matrix recommends
  "Discard" for this entry; the bulk slice does not
  commit the duplicate.
- **Rationale**: the file is a duplicate of the
  spec already shipped in Phase 3 (44f60fb).
  Committing it would create a duplicate tracked
  copy, which is bad data hygiene.
- **Alternatives considered**: commit the duplicate
  anyway (rejected — duplicates the shipped spec).
  Move the duplicate to a `discarded/` folder
  (rejected — adds a new tracked folder for an
  untracked file).

### Decision 3: Update Phase 6 docs in the same slice

- **Decision**: update
  `docs/00-project/wip-disposition-matrix.md`,
  `docs/00-project/change-queue.md`, and
  `docs/00-project/dirty-worktree-triage-report.md`
  in the same slice. Mark the absorbed entries as
  done. Add a "Deferred entries" section for the
  D + E classes.
- **Rationale**: the Phase 6 docs are the
  human-readable record of the dirty worktree; if
  the bulk slice does not update them, the docs
  become stale.
- **Alternatives considered**: update the docs in a
  separate Phase 8 (rejected — the docs and the
  absorbed entries should land together).

### Decision 4: Per-path `git add` list is
explicit, not glob

- **Decision**: the plan enumerates every A + B
  path. The implementation uses
  `git add <path>` for each path. No `git add .`
  or `git add -A`. No `git add -u` either (that
  would only stage modified tracked files, missing
  the untracked archive folders and untracked
  source/spec/test files).
- **Rationale**: the per-path list is the only way
  to satisfy the strict-scope rule and the
  dirty-worktree rule simultaneously.
- **Alternatives considered**: `git add -A`
  (rejected — includes D + E + forbidden paths).
  `git add -u` (rejected — misses untracked files).

### Decision 5: Push after the commit lands, not
before

- **Decision**: the local commit is created first;
  the verification report records the SHA; then the
  commit is pushed to `origin/main`. A follow-up
  docs commit is created to record the SHA in the
  report and the verification; the follow-up docs
  commit is also pushed.
- **Rationale**: the user wants the SHA recorded in
  the docs (per the Phase 3-6 pattern). The
  follow-up docs commit is a separate commit so the
  SHA in the bulk-slice commit's verification.md is
  stable.
- **Alternatives considered**: push the bulk-slice
  commit, then create the follow-up docs commit,
  then push it (rejected — the bulk-slice
  verification.md would not have the SHA in the
  pre-push form; the user wants the SHA in the
  shipped docs).

## Data Contracts

No schema changes. The phase is a code-import phase
that adopts existing dirty-worktree content; it does
not introduce new schemas or modify existing ones.

### `wip-disposition-matrix.md` (updated file)

The matrix gains a new "Status" column or an
"Absorbed by" annotation per entry, recording that
the entry was absorbed by
`bulk-import-pre-existing-wip` (or, for the skipped
duplicate, "skipped per matrix recommendation").

### `change-queue.md` (updated file)

The queue's 20-entry table gains a new "Status"
column or an "Absorbed by" annotation, recording
that the future change was absorbed by
`bulk-import-pre-existing-wip`.

### `dirty-worktree-triage-report.md` (updated file)

The report gains a new "Phase 7 Bulk Slice" section
that records the bulk-slice commit, the SHA, the
deferred D + E entries, and the push confirmation.

### `bulk-import-verification-report.md` (new file)

A new top-level doc that records the Phase 7
verification command results and the Phase 7 commit
SHA, following the Phase 3-6 pattern.

## Module Boundaries

### Added

- `openspec/changes/bulk-import-pre-existing-wip/.openspec.yaml`:
  the OpenSpec change skeleton header.
- `openspec/changes/bulk-import-pre-existing-wip/brainstorm.md`:
  the brainstorm artifact.
- `openspec/changes/bulk-import-pre-existing-wip/proposal.md`:
  the proposal artifact.
- `openspec/changes/bulk-import-pre-existing-wip/design.md`:
  this file.
- `openspec/changes/bulk-import-pre-existing-wip/review.md`:
  the review artifact (verdict `approve`).
- `openspec/changes/bulk-import-pre-existing-wip/plan.md`:
  the executable plan.
- `openspec/changes/bulk-import-pre-existing-wip/tasks.md`:
  the checkbox-tracked task list.
- `openspec/changes/bulk-import-pre-existing-wip/verification.md`:
  the OpenSpec-level evidence record.
- `openspec/changes/bulk-import-pre-existing-wip/specs/pre-existing-wip-bulk-import/spec.md`:
  the new capability spec.
- `docs/00-project/bulk-import-verification-report.md`:
  the top-level narrative.
- 11 untracked
  `openspec/changes/archive/2026-05-*/` folders.
- 6 untracked `openspec/specs/*/spec.md` files
  (`content-quality-rules`, `experience-accumulation`,
  `intelligent-generation-fallback`,
  `skill-adoption-workflow`, `skill-lifecycle-index`,
  `skill-promotion-and-rollback`).
- 10 untracked `src/skill_forge/**` source modules
  (`adoption/__init__.py`, `adoption/service.py`,
  `experience/__init__.py`, `experience/service.py`,
  `lifecycle/__init__.py`, `lifecycle/models.py`,
  `lifecycle/promotion.py`, `lifecycle/service.py`,
  `models/experience.py`, `retrieval/generation.py`).
- 4 untracked `tests/test_*.py` files
  (`test_experience.py`, `test_lifecycle.py`,
  `test_promotion.py`, `test_skill_adoption.py`).
- 1 untracked doc
  `docs/skill_lifecycle_governance_plan.md`.

### Modified

- 7 `openspec/specs/*/spec.md` files
  (`generation-quality-report`, `llm-assisted-generation`,
  `local-skill-generation`, `search-retrieval`,
  `skill-evaluation`, `skill-library-management`,
  `skill-validation`).
- 9 `src/skill_forge/**/*.py` files (`cli.py`,
  `config.py`, `llm/refiner.py`, `models/generated.py`,
  `models/quality.py`, `models/search.py`,
  `retrieval/retriever.py`,
  `storage/corpus_reader.py`, `storage/paths.py`).
- 5 `tests/test_*.py` files (`test_cli.py`,
  `test_generation_quality_report.py`,
  `test_llm_refiner.py`, `test_search_retrieval.py`,
  `test_skill_library.py`).
- 3 `docs/00-project/*.md` files
  (`wip-disposition-matrix.md`,
  `change-queue.md`,
  `dirty-worktree-triage-report.md`) — these are
  the Phase 6 docs that the bulk slice updates to
  mark the absorbed entries as done.

### Deleted

- 7 files under
  `openspec/changes/add-community-skill-discovery/`
  (the active change folder is being deleted because
  it has been archived; the archived copy is being
  added in the same commit).

### Untouched

- Every D-class entry: `.claude/**` and `.codex/**`
  (deferred to a future `.gitignore` change).
- Every E-class entry: `AGENT.md`,
  `docs/intelligent-generation-design.md`,
  `docs/intelligent-generation-design-v2.md`,
  `docs/intelligent-generation-roadmap.md`,
  `docs/rectification/skill-forge-phase-*-taskbook.md`
  (7 files), `docs/release-notes.md`, the 2 modified
  WIP doc files (`docs/skill_forge_next_evolution_plan.md`,
  `docs/skill_generation_roadmap.md`).
- The duplicate spec
  `openspec/specs/skill-lifecycle-recommendation/spec.md`
  (matrix entry #84) — skipped per recommendation.
- Every pre-existing Phase 0-6 OpenSpec change folder.
- Every pre-existing governance doc outside the
  strict-scope list.
- `pyproject.toml`, `uv.lock`, `templates/**`,
  `configs/**`, `scripts/**`, `README*`, `AGENTS*`/
  `CODEX*`/`CLAUDE*`/`OPENCODE*`/`SUPERPOWERS*`,
  `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`, `openspec/config.yaml`,
  `openspec/schemas/**`.

## Compatibility Impact

- Claude Code: no effect. The bulk slice adopts
  pre-existing dirty worktree; it does not introduce
  new behaviors.
- Codex: no effect.
- opencode: no effect.
- Generated Skill packages: no effect.

## Offline and Deterministic Mode

- Network unavailable: the bulk slice is a
  mechanical `git add` / `git commit` / `git push`
  workflow. The push requires network access. If
  the push fails, the local commit is preserved
  and the user can retry the push.
- LLM disabled: the bulk slice does not invoke the
  LLM.
- LLM enabled but config missing: the bulk slice
  does not invoke the LLM.

## Security and Filesystem

- Reads: `git status --short` and
  `git diff --name-only` to enumerate the dirty
  worktree; the Phase 6 matrix to identify the
  A + B entries.
- Writes: the 9 new OpenSpec change files, the
  1 new top-level doc, the 3 updated Phase 6 docs,
  the 7 modified tracked files, the 21 newly
  tracked untracked entries (1 doc + 6 specs +
  10 source + 4 tests), the 7 deletions, the
  11 archive folders (with ~54 files inside).
  The total commit size is ~70+ files.
- Environment variables: `GIT_SSH_COMMAND` may
  apply if the user uses a non-default SSH key.
- Push: `git push origin main` to the remote
  `git@github.com:zhiwuli0228/skill-forge.git`. The
  push is irreversible; a force-push would be the
  only rollback and is not performed.

## Risks / Trade-offs

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

## Migration Plan

### Deploy

1. Create the 9 new OpenSpec change files and the
   1 new top-level doc.
2. Update the 3 Phase 6 docs.
3. Stage every A + B entry with explicit
   `git add <path>`.
4. Verify the staged set with
   `git diff --cached --stat` and
   `git diff --cached --name-only`.
5. Commit with the message
   `docs: bulk import pre-existing wip`.
6. Create the follow-up docs commit with the SHA.
7. Push both commits to `origin/main` with
   `git push origin main`.

### Rollback

1. `git reset --soft HEAD~2` (or
   `git reset --mixed HEAD~2`) to undo both commits
   without losing the working tree.
2. `git push --force-with-lease origin main` to
   rewrite the remote, but this requires explicit
   user confirmation and is a destructive action.
3. The skipped duplicate spec
   (`openspec/specs/skill-lifecycle-recommendation/spec.md`)
   is unaffected; it remains untracked.
4. The deferred D + E entries are unaffected by
   the rollback.

## Open Questions

- [non-blocking] Should the bulk-slice commit be
  one commit or two? Recommend: one commit plus a
  follow-up docs commit (mirroring the Phase 3-6
  pattern).
- [non-blocking] Should the Phase 6 docs be updated
  in the same commit or in a separate commit?
  Recommend: in the same commit, so the docs and
  the absorbed entries land together.
- [non-blocking] Should the bulk slice push the
  pre-existing Phase 0-6 commits? Recommend: no, the
  user said "push after every future change" which
  applies to Phase 7+ commits only. The Phase 0-6
  commits stay local.
