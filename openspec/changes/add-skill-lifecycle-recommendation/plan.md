# Plan: add-skill-lifecycle-recommendation

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, specs/skill-lifecycle-recommendation/spec.md, design.md, review.md
>
> The plan is the executable contract between the planning
> agent and the implementation agent. It is runnable by a
> weaker agent that has not seen the conversation history.

## Change Id

`add-skill-lifecycle-recommendation`

## Allowed Paths

- `openspec/changes/add-skill-lifecycle-recommendation/.openspec.yaml`
- `openspec/changes/add-skill-lifecycle-recommendation/brainstorm.md`
- `openspec/changes/add-skill-lifecycle-recommendation/proposal.md`
- `openspec/changes/add-skill-lifecycle-recommendation/design.md`
- `openspec/changes/add-skill-lifecycle-recommendation/review.md`
- `openspec/changes/add-skill-lifecycle-recommendation/plan.md`
- `openspec/changes/add-skill-lifecycle-recommendation/tasks.md`
- `openspec/changes/add-skill-lifecycle-recommendation/verification.md`
- `openspec/changes/add-skill-lifecycle-recommendation/specs/skill-lifecycle-recommendation/spec.md`
- `src/skill_forge/lifecycle/recommendation_rules.py`
- `tests/test_lifecycle_recommendation_rules.py`
- `docs/00-project/first-governed-change-verification-report.md`

## Forbidden Paths

- `AGENTS.md`
- `CODEX.md`
- `CLAUDE.md`
- `OPENCODE.md`
- `SUPERPOWERS.md`
- `README.md`
- `README.zh-CN.md`
- `docs/03-openspec/**`
- `docs/04-superpowers/**`
- `.superpowers/**`
- `openspec/config.yaml`
- `openspec/schemas/**`
- `openspec/changes/example-governance-stack-walkthrough/**`
- `templates/**`
- `configs/**`
- `pyproject.toml`
- `uv.lock`
- Every other file under `src/skill_forge/lifecycle/` that is
  not `recommendation_rules.py` (i.e., the existing
  `__init__.py`, `models.py`, `service.py`, `recommendation.py`,
  and `promotion.py` are not modified by this slice).
- Every other file under `tests/` that is not
  `test_lifecycle_recommendation_rules.py`.
- Every other file under `docs/00-project/` that is not
  `first-governed-change-verification-report.md`.

## Pre-Conditions

- [x] `review.md` verdict is `approve`.
- [x] Working tree may contain pre-existing dirty WIP. The
      implementation must not reset, delete, or include those
      WIP files in the Phase 3 commit. The implementation must
      use explicit `git add <file>` commands and must not use
      `git add .` or `git add -A`.
- [x] The required tools are present: `openspec` CLI (from the
      npm global path), `git`, `uv`, `pytest`.

## Steps

### Step 1: Update `.openspec.yaml`

- **Files**: `openspec/changes/add-skill-lifecycle-recommendation/.openspec.yaml`.
- **Action**: change the `schema` value from `spec-driven` to
  `skill-forge-governance`. Add an `updated:` line with today's
  date.
- **Verification**:
  - Command: `cat openspec/changes/add-skill-lifecycle-recommendation/.openspec.yaml`
  - Expected exit code: 0
  - Expected observation: first line is `schema: skill-forge-governance`.
- **Escalation**: stop and report if the file is read-only or
  the path does not exist.

### Step 2: Write the four pre-existing artifacts in the new format

- **Files**:
  - `openspec/changes/add-skill-lifecycle-recommendation/proposal.md`
  - `openspec/changes/add-skill-lifecycle-recommendation/design.md`
  - `openspec/changes/add-skill-lifecycle-recommendation/tasks.md`
  - `openspec/changes/add-skill-lifecycle-recommendation/specs/skill-lifecycle-recommendation/spec.md`.
- **Action**: rewrite each file to follow the corresponding
  template under `openspec/schemas/skill-forge-governance/templates/`.
  Each file starts with `> Status: draft` and `> Schema: skill-forge-governance`
  on the first three lines.
- **Verification**:
  - Command: `ls openspec/changes/add-skill-lifecycle-recommendation/`
  - Expected exit code: 0
  - Expected observation: `proposal.md`, `design.md`,
    `tasks.md`, and `specs/skill-lifecycle-recommendation/spec.md`
    are all present.
- **Escalation**: stop and report if any of the four files is
  missing after the rewrite.

### Step 3: Add the four new artifacts

- **Files**:
  - `openspec/changes/add-skill-lifecycle-recommendation/brainstorm.md`
  - `openspec/changes/add-skill-lifecycle-recommendation/review.md`
  - `openspec/changes/add-skill-lifecycle-recommendation/plan.md`
  - `openspec/changes/add-skill-lifecycle-recommendation/verification.md`.
- **Action**: write each file. The `verification.md` is the
  last artifact and is written after the implementation and
  tests pass.
- **Verification**:
  - Command: `ls openspec/changes/add-skill-lifecycle-recommendation/`
  - Expected exit code: 0
  - Expected observation: the eight artifact files are
    present.
- **Escalation**: stop and report if any file is missing.

### Step 4: Add the pure function module

- **Files**: `src/skill_forge/lifecycle/recommendation_rules.py`.
- **Action**: define `LifecycleRecommendationInput` (Pydantic
  model with `extra="forbid"` and the field set described in
  `design.md`) and `recommend_lifecycle_action` (module-level
  pure function that takes the input model and returns the
  existing `LifecycleRecommendation` from
  `skill_forge.lifecycle.recommendation`).
- **Verification**:
  - Command: `python -c "import skill_forge.lifecycle.recommendation_rules; print('ok')"`
  - Expected exit code: 0
  - Expected observation: the import succeeds and prints
    `ok`.
- **Escalation**: stop and report on any
  `ImportError` or `SyntaxError`.

### Step 5: Add the unit test file

- **Files**: `tests/test_lifecycle_recommendation_rules.py`.
- **Action**: write at least the five required test cases
  (unknown state, outdated provenance, current valid metadata,
  invalid or incomplete input, deterministic behavior).
- **Verification**:
  - Command: `uv run pytest tests/test_lifecycle_recommendation_rules.py -v`
  - Expected exit code: 0
  - Expected observation: every test in the new file passes.
- **Escalation**: if any test fails, apply
  `systematic-debugging` from `SUPERPOWERS.md` (reproduce,
  locate root cause, fix, do not modify the test to match a
  broken implementation).

### Step 6: Run the full verification suite

- **Files**: none (read-only commands).
- **Action**: run the final verification commands listed in
  the "Final Verification" section below.
- **Verification**:
  - Command: see "Final Verification" below.
  - Expected exit code: 0 for every command.
  - Expected observation: every command succeeds and the
    change is included in the passed list.
- **Escalation**: if any command fails, stop and report. Do
  not paper over the failure.

### Step 7: Write `verification.md`

- **Files**:
  - `openspec/changes/add-skill-lifecycle-recommendation/verification.md`
  - `docs/00-project/first-governed-change-verification-report.md`.
- **Action**: write both files. The change-folder
  `verification.md` records the OpenSpec-level evidence
  record. The docs-level report is a human-readable summary
  written for the Phase 3 commit.
- **Verification**:
  - Command: `cat openspec/changes/add-skill-lifecycle-recommendation/verification.md | head -20`
  - Expected exit code: 0
  - Expected observation: the file starts with `> Status: draft`
    and `> Schema: skill-forge-governance`.
- **Escalation**: stop and report if the file cannot be
  written.

### Step 8: Commit only Phase 3 files

- **Files**: every file under the allowed-path list that
  actually changed in this phase, plus the two new files
  under `docs/00-project/` (the verification report).
- **Action**: use explicit `git add <path>` commands for each
  file. Do not use `git add .` or `git add -A`. Commit with
  the message
  `feat: add governed skill lifecycle recommendation slice`.
- **Verification**:
  - Command: `git show --stat HEAD`
  - Expected exit code: 0
  - Expected observation: the commit's file list matches the
    Phase 3 file list. No pre-existing WIP file is included.
- **Escalation**: if `git show --stat HEAD` reports a file
  that is not in the Phase 3 file list, stop and report. Do
  not amend the commit.

## Final Verification

- Command: `git status --short`
- Command: `git diff --name-only`
- Command: `openspec validate add-skill-lifecycle-recommendation --strict`
- Command: `openspec validate --strict --all`
- Command: `uv run pytest`
- Command: `uv run skill-forge --help`

## Rollback

1. Reset the working tree to `HEAD` (do not run
   `git reset --hard` before the commit; if the commit has
   landed, run `git revert HEAD` instead).
2. If the revert is not possible because the commit has
   already been pushed, run `git revert HEAD` and push the
   revert.
3. No data migration. The pure function is in-memory only and
   did not write to disk.
4. If a follow-up change wants to keep any of the new OpenSpec
   artifacts, cherry-pick them individually rather than
   reverting the whole commit.

## Hand-off Note

- The single most important rule for this change is: **the
  pure function does no I/O**. Every test, every artifact, and
  every commit must respect that boundary. If a step needs to
  read a file or call a service, stop and report; the slice
  is the pure function, not a wrapper.
