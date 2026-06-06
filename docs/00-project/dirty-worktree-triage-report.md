# Dirty Worktree Triage Report

> Status: draft
> Schema: skill-forge-governance
> Phase: 6
> Date: 2026-06-06
> Companion to:
> `docs/00-project/wip-disposition-matrix.md` and
> `docs/00-project/change-queue.md`
> OpenSpec change:
> `openspec/changes/triage-dirty-worktree-change-queue/`
> Commit SHA: see "Commit SHA" section
>
> This report records the audit and normalization of
> the dirty working tree and the future change queue.
> The phase is documentation-only. It does not
> implement features, does not delete or reset user
> WIP, and does not modify any pre-existing OpenSpec
> change, source file, test, template, config, or
> script.

## 1. Phase 6 Goal

Audit the existing dirty working tree, classify every
dirty entry into one of five buckets, list the
recommended future OpenSpec changes in priority order,
and produce a single governance record
(`openspec/changes/triage-dirty-worktree-change-queue/`)
plus three doc files
(`wip-disposition-matrix.md`, `change-queue.md`, and
this report). The phase is a normalization slice; it
must not implement features.

## 2. Methodology

The triage is based on the four git commands
recommended in the Phase 6 task:

1. `git status --short` — enumerates every modified,
   deleted, and untracked entry.
2. `git diff --name-only` — enumerates the
   paths of every modified tracked file.
3. `git ls-files --others --exclude-standard` —
   enumerates every untracked entry that is not
   excluded by `.gitignore`.
4. `git diff --stat` — records the per-file line
   counts for every modified tracked file.
5. `git log --oneline -10` — records the recent
   commit history for traceability.

The classification scheme is the A/B/C/D/E rubric
defined in
`openspec/changes/triage-dirty-worktree-change-queue/design.md`
(Decision 1) and reproduced in
`docs/00-project/wip-disposition-matrix.md`. The
recommended change queue is the future OpenSpec
change ordering in `docs/00-project/change-queue.md`.

## 3. Git State Snapshot (Phase 6 start)

The commands were run from the repository root on
2026-06-06, after Phase 5 commit `e4992be` and before
the Phase 6 commit.

### 3.1 `git log --oneline -10`

```
e4992be docs: record Phase 5 commit SHA in verification report
2cb3912 refactor: reuse lifecycle recommendation rules in service
39941f3 docs: record Phase 4 commit SHA in verification report
0bcd73f chore: add governance enforcement check
1ace0e9 docs: record Phase 3 commit SHA in verification report
44f60fb feat: add governed skill lifecycle recommendation slice
848ce55 docs: integrate superpowers execution discipline
a14a4d4 docs: introduce openspec superspec governance schema
e541b3b docs: establish governance entry points
6c05450 chore: initial commit
```

### 3.2 `git status --short` summary

- **30** modified tracked files
  (`M` prefix; details in matrix §1).
- **8** deletions under
  `openspec/changes/add-community-skill-discovery/`
  (`D` prefix; details in matrix §1, entries #3-#9).
- **~70** untracked entries spanning `.claude/`,
  `.codex/`, `AGENT.md`, `docs/`,
  `openspec/changes/archive/`, `openspec/specs/`,
  `src/`, and `tests/`. See matrix §2-§7 for the
  per-entry breakdown.

### 3.3 `git diff --stat` summary

30 files changed, ~2249 insertions, ~398 deletions.
The largest changes are in `src/skill_forge/cli.py`
(+662), `src/skill_forge/llm/refiner.py` (+243),
`src/skill_forge/models/quality.py` (+221),
`tests/test_cli.py` (+316), and
`tests/test_llm_refiner.py` (+161). All of these
are B-class (candidate for future governed change).

## 4. WIP Classification Summary

| Class | Count | Description |
|-------|-------|-------------|
| A. Absorbed by prior phases | 18 | Already represented in a committed change or in a working-tree archive copy of a committed change. |
| B. Candidate for future governed change | 56 | New source modules, new specs, new tests, or large modifications to existing modules that need an OpenSpec change to be properly tracked. |
| C. Existing change needs reshape | 0 | (None observed in the Phase 6 dirty worktree.) |
| D. Candidate for discard | 24 | Local tool directories (`.claude/`, `.codex/`) that should be added to `.gitignore` via a follow-up change, plus one superseded design doc. |
| E. Requires user decision | 14 | WIP doc edits, top-level agent file, rectification taskbooks, release notes, and evolution-plan doc edits. |
| **Total** | **112** | All dirty entries. |

The full per-entry table is in
`docs/00-project/wip-disposition-matrix.md`.

## 5. Recommended Change Queue Summary

The change queue has 20 entries (1-20). The first
3 are small cleanup changes; entries 4-12 are
substantive re-derivations of the archived changes
plus the new untracked modules; entries 13-14 are
follow-up governance and CLI changes; entries 15-19
are user-decision items; entry 20 is the already-shipped
Phase 5 consolidation. See
`docs/00-project/change-queue.md` for the full table.

The recommended sequencing is documented in §2 of
`docs/00-project/change-queue.md`. The B-class
entries are interleaved with the small A-class
cleanup entries at the start because the cleanup
makes the working tree navigable for the substantive
re-derivations.

## 6. Changed Files (Phase 6)

The following files are created by this phase. No
pre-existing file is modified.

- `openspec/changes/triage-dirty-worktree-change-queue/.openspec.yaml`
- `openspec/changes/triage-dirty-worktree-change-queue/brainstorm.md`
- `openspec/changes/triage-dirty-worktree-change-queue/proposal.md`
- `openspec/changes/triage-dirty-worktree-change-queue/design.md`
- `openspec/changes/triage-dirty-worktree-change-queue/review.md`
- `openspec/changes/triage-dirty-worktree-change-queue/plan.md`
- `openspec/changes/triage-dirty-worktree-change-queue/tasks.md`
- `openspec/changes/triage-dirty-worktree-change-queue/verification.md`
- `openspec/changes/triage-dirty-worktree-change-queue/specs/dirty-worktree-change-queue/spec.md`
- `docs/00-project/dirty-worktree-triage-report.md` (this file)
- `docs/00-project/wip-disposition-matrix.md`
- `docs/00-project/change-queue.md`

Total: 12 new files. Zero modifications to pre-existing
files.

## 7. Restricted Path Check

The Phase 6 strict-scope allowed-path list was
respected. None of the forbidden paths listed in
the Phase 6 task were touched. The following paths
are explicitly **not** in the Phase 6 diff:

- `src/**` (untouched).
- `tests/**` (untouched).
- `templates/**` (untouched).
- `configs/**` (untouched).
- `scripts/**` (untouched).
- `pyproject.toml` (untouched).
- `uv.lock` (untouched).
- `README.md`, `README.zh-CN.md` (untouched).
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
  `SUPERPOWERS.md` (untouched).
- `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**` (untouched).
- `openspec/config.yaml`, `openspec/schemas/**`
  (untouched).
- Every pre-existing
  `openspec/changes/<existing-change-id>/` folder
  (active or archived), including
  `openspec/changes/add-skill-lifecycle-recommendation/`,
  `openspec/changes/add-governance-enforcement-hooks/`,
  `openspec/changes/consolidate-lifecycle-recommendation-service/`,
  `openspec/changes/example-governance-stack-walkthrough/`,
  and every folder under
  `openspec/changes/archive/` (untouched).
- Every other `docs/00-project/**` file
  (untouched; the only created file under
  `docs/00-project/` is this report, plus the two
  companion doc files).

Verdict: **forbidden paths changed: no**.

## 8. Dirty Worktree Handling

The pre-existing dirty worktree at the start of
Phase 6 was 30 modified tracked files, 8 deletions
under
`openspec/changes/add-community-skill-discovery/`,
and ~70 untracked entries. The dirty worktree was
preserved untouched. The phase recorded the
disposition of every dirty entry in the matrix; it
did not delete, reset, restore, or clean any
entry.

The Phase 6 commit is staged with explicit
`git add <path>` commands for each of the 12
allowed-path files. No `git add .` or `git add -A`
is used. None of the pre-existing dirty entries
are included in the Phase 6 commit.

The recommended future change queue records how a
future phase may absorb the B-class entries into
new OpenSpec changes. The D-class entries are
deferred to a future `.gitignore` change. The
E-class entries are deferred to a user decision.
The A-class entries are kept as-is; the only
follow-up action is to commit the untracked archive
folders and the tracked deletions in a future
docs commit.

## 9. OpenSpec Change Summary

The change folder
`openspec/changes/triage-dirty-worktree-change-queue/`
declares
`schema: skill-forge-governance` and contains the
full nine artifacts:

- `.openspec.yaml`
- `brainstorm.md`
- `proposal.md`
- `design.md`
- `review.md`
- `plan.md`
- `tasks.md`
- `verification.md`
- `specs/dirty-worktree-change-queue/spec.md`

The capability name in the proposal matches the
spec file folder
(`dirty-worktree-change-queue`). The change adds
one new capability
(`dirty-worktree-change-queue`) and does not modify
any existing capability.

The `review.md` verdict is `approve`. The `plan.md`
is the executable contract and lists the allowed
and forbidden paths explicitly. The `verification.md`
is the OpenSpec-level evidence record for the change.

## 10. Verification Command Results

| Command                                                                       | Exit Code | Output Summary                                                                                                            |
|-------------------------------------------------------------------------------|-----------|---------------------------------------------------------------------------------------------------------------------------|
| `git status --short`                                                          | 0         | The pre-existing dirty worktree (30 modified, 8 deleted, ~70 untracked) is visible. The Phase 6 files are not yet listed at the time of the run. |
| `git diff --name-only`                                                        | 0         | The 30 modified tracked files are listed; the Phase 6 files are not in this list because they are untracked at the time of the run. |
| `git ls-files --others --exclude-standard`                                    | 0         | The ~70 untracked entries are listed; the Phase 6 files are not in this list because they are created after the run. |
| `git diff --stat`                                                             | 0         | 30 files changed, ~2249 insertions, ~398 deletions. |
| `git log --oneline -10`                                                       | 0         | The 10 most recent commits, ending at `e4992be docs: record Phase 5 commit SHA in verification report`. |
| `openspec validate triage-dirty-worktree-change-queue --strict`               | 0         | `Change 'triage-dirty-worktree-change-queue' is valid`. |
| `openspec validate --strict --all`                                            | 0         | 27+ items passed, 0 failed. The new change is included in the passed list. |
| `python scripts/governance_check.py --quick`                                  | 0         | `[PASS] openspec validate --strict --all (required)` + `[PASS] uv run skill-forge --help (required)`, summary `2 passed, 0 failed, 0 skipped`. |
| `python scripts/governance_check.py` (recommended)                            | 0         | 6 PASS lines, summary `6 passed, 0 failed, 0 skipped`. |
| `uv run pytest` (recommended)                                                 | 0         | 310 passed in 13.92s. (Same as Phase 5; the dirty worktree additions are not yet exercised.) |
| `uv run skill-forge --help` (recommended)                                     | 0         | Exit 0; the pre-existing `lifecycle` command is unchanged. |

## 11. Quick and Full Governance Check Results

### 11.1 Quick mode (`--quick`)

- `[PASS] openspec validate --strict --all (required)`
- `[PASS] uv run skill-forge --help (required)`
- `Summary: 2 passed, 0 failed, 0 skipped`
- Exit code: 0

### 11.2 Full mode (default)

- `[PASS] openspec schema validate (required)`
- `[PASS] openspec validate example-governance-stack-walkthrough --strict (required)`
- `[PASS] openspec validate add-skill-lifecycle-recommendation --strict (required)`
- `[PASS] openspec validate --strict --all (required)`
- `[PASS] uv run skill-forge --help (required)`
- `[PASS] uv run pytest (required)`
- `Summary: 6 passed, 0 failed, 0 skipped`
- Exit code: 0

## 12. Skipped Commands and Reasons

No commands in the script's command list were
skipped during the recorded runs. The optional-skip
path is exercised by the unit tests but did not
trigger during this verification.

## 13. Implementation Notes

- The matrix uses the `A (untracked)` status to
  distinguish untracked entries from `M` (modified)
  tracked entries. This makes the per-entry table
  greppable.
- The change queue references the matrix entry
  numbers in the "Source buckets" column. The
  reference is one-way; a future change may extend
  the matrix without breaking the queue.
- The phase is intentionally documentation-only. No
  source code, test, template, config, script, or
  pre-existing OpenSpec change is modified. The
  actual change is the work of a future OpenSpec
  change.

## 14. Remaining Risks

- [The matrix and the queue may drift from the
  actual dirty worktree over time] -> Mitigation:
  the verification.md is the source of truth; the
  matrix and the queue are generated from a
  one-time snapshot taken at the start of Phase 6,
  and any drift is recorded as a follow-up entry
  in the matrix.
- [The recommended change queue order may not
  match the user's actual priorities] ->
  Mitigation: the queue records the recommended
  order and the blocking dependency, but it is
  advisory; the user can reorder it.
- [The strict-scope allowed-path list may exclude
  a file the user wants to add to the matrix] ->
  Mitigation: the matrix lives entirely in
  `docs/00-project/wip-disposition-matrix.md` and
  is a plain markdown table; the user can extend
  it without touching any other file.
- [The `.claude/` and `.codex/` directories are
  recorded as `D` but a follow-up change is needed
  to add them to `.gitignore`] -> Mitigation: the
  matrix explicitly lists the follow-up change in
  the change queue as
  `add-local-tool-gitignore-excludes`.
- [The D-class and E-class entries are advisory,
  not authoritative] -> Mitigation: the matrix
  records the recommended action; the user can
  override the recommendation.

## 15. Commit Recommendation

The change is recommended for commit. The OpenSpec
validation, the quick governance check, the full
governance check, the test suite (310 tests), and
the CLI smoke test all pass. The Phase 6 forbidden
paths are untouched. The pre-existing dirty
worktree is preserved. The slice is a small,
additive, documentation-only normalization.

## 16. Commit SHA

The Phase 6 change is committed as `351cc7e` (short
SHA; full SHA: see `git show 351cc7e`) with the
message `docs: triage dirty worktree change queue`.
The commit was prepared with explicit
`git add <path>` commands for each of the 12 Phase 6
paths; no `git add .` or `git add -A` was used. The
pre-existing dirty worktree is preserved untouched
and is not included in the commit. A follow-up docs
commit records the SHA in this report and in
`openspec/changes/triage-dirty-worktree-change-queue/verification.md`.
