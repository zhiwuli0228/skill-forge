# Plan: bulk-import-pre-existing-wip

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md, design.md, review.md
>
> The plan is the executable contract between the
> planning agent and the implementation agent. It must
> be runnable by a weaker agent that has not seen the
> conversation history.

## Change Id

`bulk-import-pre-existing-wip`

## Allowed Paths

The allowed paths are the strict-scope list for this
slice. See `review.md` for the full enumeration. In
summary:

- `openspec/changes/bulk-import-pre-existing-wip/**`
  (the new OpenSpec change folder).
- `docs/00-project/bulk-import-verification-report.md`
  (the new top-level doc).
- `docs/00-project/wip-disposition-matrix.md`,
  `docs/00-project/change-queue.md`,
  `docs/00-project/dirty-worktree-triage-report.md`
  (the three updated Phase 6 docs).
- 7 deletions under
  `openspec/changes/add-community-skill-discovery/`.
- 11 archive folders under
  `openspec/changes/archive/2026-05-*/`.
- 21 modified tracked B-class files (7
  `openspec/specs/*/spec.md`, 9 `src/skill_forge/**/*.py`,
  5 `tests/test_*.py`).
- 21 untracked B-class files (1 doc, 6 specs, 10
  source modules, 4 test files).

## Forbidden Paths

- Every D-class entry: `.claude/**` and `.codex/**`.
- Every E-class entry: `AGENT.md`,
  `docs/intelligent-generation-design.md`,
  `docs/intelligent-generation-design-v2.md`,
  `docs/intelligent-generation-roadmap.md`,
  `docs/rectification/skill-forge-phase-*-taskbook.md`
  (7 files), `docs/release-notes.md`,
  `docs/skill_forge_next_evolution_plan.md`,
  `docs/skill_generation_roadmap.md`.
- The duplicate spec
  `openspec/specs/skill-lifecycle-recommendation/spec.md`.
- Every pre-existing Phase 0-6 OpenSpec change
  folder.
- `pyproject.toml`, `uv.lock`, `templates/**`,
  `configs/**`, `scripts/**`, `README*`, `AGENTS*`/
  `CODEX*`/`CLAUDE*`/`OPENCODE*`/`SUPERPOWERS*`,
  `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`, `openspec/config.yaml`,
  `openspec/schemas/**`.
- Every other `docs/00-project/**` file.

## Pre-Conditions

- [x] `review.md` verdict is `approve`.
- [x] Working tree is dirty with the Phase 6
      classified entries; the A + B entries are
      available for staging.
- [x] The remote is configured:
      `git@github.com:zhiwuli0228/skill-forge.git`.
- [x] The local branch is `main`.
- [x] The required tools are present: `git`,
      `openspec` CLI, `python` (for
      `scripts/governance_check.py`), `uv` (for
      `uv run pytest` and `uv run skill-forge --help`).

## Steps

### Step 1: Create the OpenSpec change skeleton

- **Files**: the 9 new files under
  `openspec/changes/bulk-import-pre-existing-wip/`
  (the `.openspec.yaml` header, the eight
  governance artifacts, and the new spec file
  under
  `specs/pre-existing-wip-bulk-import/spec.md`).
- **Action**: write each artifact in turn,
  following the templates under
  `openspec/schemas/skill-forge-governance/templates/`.
  The spec adds the new capability
  `pre-existing-wip-bulk-import`. The review verdict
  is `approve`. The plan is this file.
- **Verification**:
  - Command: `openspec validate bulk-import-pre-existing-wip --strict`
  - Expected exit code: `0`
  - Expected observation:
    `Change 'bulk-import-pre-existing-wip' is valid`.
- **Escalation**: if validation fails, fix the
  failing artifact per the validator's error
  message; do not proceed until validation passes.

### Step 2: Update the Phase 6 docs

- **Files**:
  `docs/00-project/wip-disposition-matrix.md`,
  `docs/00-project/change-queue.md`,
  `docs/00-project/dirty-worktree-triage-report.md`.
- **Action**: add a "Phase 7 Bulk Slice" section to
  the report; mark the absorbed entries as done in
  the matrix and the queue; add a "Deferred
  entries" section for the D + E classes.
- **Verification**:
  - Command: `openspec validate --strict --all`
  - Expected exit code: `0`
  - Expected observation: 28+ items passed, 0
    failed (the new change is included in the passed
    list).
- **Escalation**: if any pre-existing spec or
  change fails validation that was passing before,
  stop and investigate; the strict-scope forbidden
  list prevents touching them, so a regression
  indicates a problem with the validator or the
  environment.

### Step 3: Stage the A + B entries

- **Files**: the 7 deletions + 11 archive folders +
  21 modified tracked + 21 untracked = ~60 paths.
- **Action**: stage every A + B entry with explicit
  `git add <path>`. No `git add .` or `git add -A`.
- **Verification**:
  - Command: `git diff --cached --stat`
  - Expected exit code: `0`
  - Expected observation: the staged set is exactly
    the A + B paths; no D + E paths; no forbidden
    paths; no duplicate spec.
- **Escalation**: if the staged set includes any
  forbidden path or D + E entry, abort the staging
  with `git restore --staged <path>`, re-stage only
  the A + B paths, and retry.

### Step 4: Run the verification commands

- **Files**: none.
- **Action**: run the verification commands listed
  in the Final Verification section below.
- **Verification**:
  - Command: `python scripts/governance_check.py`
  - Expected exit code: `0`
  - Expected observation: 6 PASS lines, summary
    `6 passed, 0 failed, 0 skipped`.
- **Escalation**: if any check fails, stop and
  investigate; do not commit or push a broken
  state.

### Step 5: Commit the bulk slice

- **Files**: the staged set from Step 3.
- **Action**: commit with the message
  `docs: bulk import pre-existing wip`. Use a
  multi-line body that lists the absorbed entries.
- **Verification**:
  - Command: `git show --stat HEAD`
  - Expected observation: the commit's changed file
    list is exactly the A + B paths.
- **Escalation**: if `git show --stat HEAD` shows any
  forbidden path or D + E entry, abort with
  `git reset --soft HEAD~1`, re-stage only the A + B
  paths, and retry.

### Step 6: Create the follow-up docs commit

- **Files**:
  `openspec/changes/bulk-import-pre-existing-wip/verification.md`
  and
  `docs/00-project/bulk-import-verification-report.md`.
- **Action**: update the verification.md and the
  report with the actual commit SHA; commit with
  the message
  `docs: record Phase 7 commit SHA in verification
  report`.
- **Verification**:
  - Command: `git show --stat HEAD`
  - Expected observation: the follow-up docs commit
    changes only the 2 files.
- **Escalation**: same as Step 5.

### Step 7: Push to `origin/main`

- **Files**: the 2 commits from Steps 5-6.
- **Action**: `git push origin main`.
- **Verification**:
  - Command: `git log --oneline origin/main -2`
  - Expected observation: the top 2 commits on
    `origin/main` are the bulk-slice commit and the
    follow-up docs commit.
- **Escalation**: if the push fails, the local
  commits are preserved. Investigate the failure
  (network, auth, remote protection); do not force
  push.

## Final Verification

- Command:
  `openspec validate bulk-import-pre-existing-wip --strict`
- Command: `openspec validate --strict --all`
- Command: `python scripts/governance_check.py --quick`
- Command: `python scripts/governance_check.py`
- Command: `uv run pytest`
- Command: `uv run skill-forge --help`
- Command: `git push origin main`

## Rollback

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
   the rollback (they were not committed in this
   slice).

## Hand-off Note

- The phase adopts pre-existing dirty-worktree
  content verbatim. It does not re-shape the B-class
  additions. It does not modify `.gitignore` or any
  E-class entry. It uses explicit `git add <path>`
  for every A + B path; no `git add .` or
  `git add -A`. The push is to `origin/main` only
  after both local commits land. The user has
  authorized the push.
