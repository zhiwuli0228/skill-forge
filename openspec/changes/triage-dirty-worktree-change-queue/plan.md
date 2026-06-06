# Plan: triage-dirty-worktree-change-queue

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, spec.md, design.md, review.md
>
> The plan is the executable contract between the
> planning agent and the implementation agent. It must
> be runnable by a weaker agent that has not seen the
> conversation history.

## Change Id

`triage-dirty-worktree-change-queue`

## Allowed Paths

- `openspec/changes/triage-dirty-worktree-change-queue/.openspec.yaml`
- `openspec/changes/triage-dirty-worktree-change-queue/brainstorm.md`
- `openspec/changes/triage-dirty-worktree-change-queue/proposal.md`
- `openspec/changes/triage-dirty-worktree-change-queue/design.md`
- `openspec/changes/triage-dirty-worktree-change-queue/review.md`
- `openspec/changes/triage-dirty-worktree-change-queue/plan.md`
- `openspec/changes/triage-dirty-worktree-change-queue/tasks.md`
- `openspec/changes/triage-dirty-worktree-change-queue/verification.md`
- `openspec/changes/triage-dirty-worktree-change-queue/specs/dirty-worktree-change-queue/spec.md`
- `docs/00-project/dirty-worktree-triage-report.md`
- `docs/00-project/wip-disposition-matrix.md`
- `docs/00-project/change-queue.md`

## Forbidden Paths

- `src/**`
- `tests/**`
- `templates/**`
- `configs/**`
- `scripts/**`
- `pyproject.toml`
- `uv.lock`
- `README.md`, `README.zh-CN.md`
- `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `OPENCODE.md`,
  `SUPERPOWERS.md`
- `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`
- `openspec/config.yaml`, `openspec/schemas/**`
- Every pre-existing
  `openspec/changes/<existing-change-id>/` folder
  (active or archived), including but not limited to
  `openspec/changes/add-skill-lifecycle-recommendation/`,
  `openspec/changes/add-governance-enforcement-hooks/`,
  `openspec/changes/consolidate-lifecycle-recommendation-service/`,
  `openspec/changes/example-governance-stack-walkthrough/`,
  and every folder under `openspec/changes/archive/`.
- Every file under `docs/00-project/**` other than
  the three allowed-path files.

## Pre-Conditions

- [x] `review.md` verdict is `approve`.
- [x] Working tree is dirty (intentionally; the
      phase is documentation-only and the dirty
      surface is recorded, not cleaned).
- [x] The required tools are present: `git`,
      `openspec` CLI, `python` (for
      `scripts/governance_check.py`), `uv` (for the
      recommended `uv run pytest` and
      `uv run skill-forge --help`).

## Steps

### Step 1: Create the OpenSpec change skeleton

- **Files**: the nine files under
  `openspec/changes/triage-dirty-worktree-change-queue/`
  (the `.openspec.yaml` header, the eight governance
  artifacts, and the new spec file under
  `specs/dirty-worktree-change-queue/spec.md`).
- **Action**: write each artifact in turn,
  following the templates under
  `openspec/schemas/skill-forge-governance/templates/`.
  The spec adds the new capability
  `dirty-worktree-change-queue`. The review verdict
  is `approve`. The plan is this file.
- **Verification**:
  - Command: `openspec validate triage-dirty-worktree-change-queue --strict`
  - Expected exit code: `0`
  - Expected observation:
    `Change 'triage-dirty-worktree-change-queue' is valid`.
- **Escalation**: if validation fails, fix the
  failing artifact per the validator's error
  message; do not proceed until validation passes.

### Step 2: Write the three doc files

- **Files**:
  `docs/00-project/wip-disposition-matrix.md`,
  `docs/00-project/change-queue.md`,
  `docs/00-project/dirty-worktree-triage-report.md`.
- **Action**: classify every dirty entry from
  `git status --short`,
  `git diff --name-only`,
  `git ls-files --others --exclude-standard`, and
  `git diff --stat` into the A/B/C/D/E buckets; list
  the recommended future OpenSpec changes in
  priority order; write the top-level narrative that
  ties the matrix and the queue together.
- **Verification**:
  - Command: `openspec validate --strict --all`
  - Expected exit code: `0`
  - Expected observation: 27+ items passed, 0 failed
    (the new change is included in the passed list).
- **Escalation**: if any pre-existing spec or change
  fails validation that was passing before, stop and
  investigate; the strict-scope forbidden list
  prevents touching them, so a regression indicates
  a problem with the validator or the environment.

### Step 3: Run the quick governance check

- **Files**: none.
- **Action**: run the quick governance check to
  confirm the Phase 6 work does not break the
  pre-existing required checks.
- **Verification**:
  - Command: `python scripts/governance_check.py --quick`
  - Expected exit code: `0`
  - Expected observation:
    `[PASS] openspec validate --strict --all (required)`
    and
    `[PASS] uv run skill-forge --help (required)`,
    summary `2 passed, 0 failed, 0 skipped`.
- **Escalation**: if any required check fails, stop
  and investigate; do not modify the dirty worktree
  to make the check pass.

### Step 4: (Recommended) Run the full governance
check, the test suite, and the CLI smoke test

- **Files**: none.
- **Action**: run the recommended verification
  commands from the task description to confirm the
  Phase 6 work does not break the pre-existing
  runtime.
- **Verification**:
  - Command: `python scripts/governance_check.py`
    -> expected summary
    `6 passed, 0 failed, 0 skipped`.
  - Command: `uv run pytest`
    -> expected summary `310 passed` (or higher if
    the pre-existing WIP tests are green in the
    environment).
  - Command: `uv run skill-forge --help`
    -> expected exit code `0`.
- **Escalation**: if any check fails, stop and
  investigate; do not modify the dirty worktree to
  make the check pass.

### Step 5: Commit only the Phase 6 files

- **Files**: the 12 allowed-path files.
- **Action**: stage the 12 allowed-path files
  explicitly with `git add <path>` (no
  `git add .` or `git add -A`), and commit with the
  suggested message
  `docs: triage dirty worktree change queue`.
- **Verification**:
  - Command: `git show --stat HEAD`
  - Expected observation: the commit's changed file
    list is exactly the 12 allowed-path files (or
    exactly the 12 files plus the follow-up docs
    commit's 2 files, if the user requests the
    follow-up).
- **Escalation**: if `git status --short` shows any
  pre-existing dirty entry in the staged set, abort
  the commit, reset the staging area with
  `git restore --staged <path>`, re-stage only the
  12 allowed-path files, and retry.

## Final Verification

- Command: `openspec validate triage-dirty-worktree-change-queue --strict`
- Command: `openspec validate --strict --all`
- Command: `python scripts/governance_check.py --quick`
- (Recommended) Command: `python scripts/governance_check.py`
- (Recommended) Command: `uv run pytest`
- (Recommended) Command: `uv run skill-forge --help`

## Rollback

1. `git reset --soft HEAD~1` (or
   `git reset --mixed HEAD~1` if the dirty worktree
   must be preserved) to undo the Phase 6 commit
   without losing the dirty worktree.
2. `rm -rf openspec/changes/triage-dirty-worktree-change-queue`
   to delete the OpenSpec change folder.
3. `rm -f docs/00-project/dirty-worktree-triage-report.md docs/00-project/wip-disposition-matrix.md docs/00-project/change-queue.md`
   to delete the three new doc files.
4. The dirty worktree is unaffected. No code, test,
   template, config, script, or pre-existing
   OpenSpec change is touched, so rollback is
   guaranteed to be safe.

## Hand-off Note

- The phase is documentation-only. Do not modify
  any file outside the 12 allowed paths. Do not
  reset, delete, restore, or clean the dirty
  worktree. Do not use `git add .` or `git add -A`;
  use explicit `git add <path>` for each of the 12
  files. The triage records the recommended
  disposition; the actual change is the work of a
  future OpenSpec change.
