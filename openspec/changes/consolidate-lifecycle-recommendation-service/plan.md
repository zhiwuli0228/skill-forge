# Plan: consolidate-lifecycle-recommendation-service

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, specs/lifecycle-recommendation-service-adapter/spec.md, design.md, review.md
>
> The plan is the executable contract between the planning
> agent and the implementation agent. It is runnable by a
> weaker agent that has not seen the conversation history.

## Change Id

`consolidate-lifecycle-recommendation-service`

## Allowed Paths

- `openspec/changes/consolidate-lifecycle-recommendation-service/.openspec.yaml`
- `openspec/changes/consolidate-lifecycle-recommendation-service/brainstorm.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/proposal.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/design.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/review.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/plan.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/tasks.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`
- `openspec/changes/consolidate-lifecycle-recommendation-service/specs/lifecycle-recommendation-service-adapter/spec.md`
- `src/skill_forge/lifecycle/recommendation.py`
- `src/skill_forge/lifecycle/recommendation_rules.py`
- `tests/test_lifecycle_recommendation.py`
- `tests/test_lifecycle_recommendation_rules.py`
- `docs/00-project/lifecycle-service-adapter-verification-report.md`

## Forbidden Paths

- `scripts/governance_check.py`
- `tests/test_governance_check.py`
- `src/skill_forge/cli.py`
- Every other file under `src/skill_forge/**` that is
  not `src/skill_forge/lifecycle/recommendation.py` or
  `src/skill_forge/lifecycle/recommendation_rules.py`.
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
- `openspec/changes/add-skill-lifecycle-recommendation/**`
- `openspec/changes/add-governance-enforcement-hooks/**`
- `templates/**`
- `configs/**`
- `pyproject.toml`
- `uv.lock`
- Every file under `tests/**` that is not
  `tests/test_lifecycle_recommendation.py` or
  `tests/test_lifecycle_recommendation_rules.py`.
- Every file under `docs/00-project/**` that is not
  `docs/00-project/lifecycle-service-adapter-verification-report.md`.

## Pre-Conditions

- [x] `review.md` verdict is `approve`.
- [x] Working tree may contain pre-existing dirty WIP.
      The implementation must not reset, delete, or
      include those WIP files in the Phase 5 commit. The
      implementation must use explicit `git add <file>`
      commands and must not use `git add .` or
      `git add -A`.
- [x] The required tools are present: `python`, `git`,
      `openspec` CLI, `uv`, `pytest`.

## Steps

### Step 1: Create the change folder skeleton

- **Files**:
  `openspec/changes/consolidate-lifecycle-recommendation-service/.openspec.yaml`.
- **Action**: create the folder and the `.openspec.yaml`
  with `schema: skill-forge-governance`, `created:` and
  `updated:` lines set to today's date.
- **Verification**:
  - Command:
    `cat openspec/changes/consolidate-lifecycle-recommendation-service/.openspec.yaml`
  - Expected exit code: 0
  - Expected observation: first line is
    `schema: skill-forge-governance`.
- **Escalation**: stop and report if the file cannot be
  written.

### Step 2: Write the eight governance artifacts

- **Files**:
  - `openspec/changes/consolidate-lifecycle-recommendation-service/brainstorm.md`
  - `openspec/changes/consolidate-lifecycle-recommendation-service/proposal.md`
  - `openspec/changes/consolidate-lifecycle-recommendation-service/design.md`
  - `openspec/changes/consolidate-lifecycle-recommendation-service/review.md`
  - `openspec/changes/consolidate-lifecycle-recommendation-service/plan.md`
  - `openspec/changes/consolidate-lifecycle-recommendation-service/tasks.md`
  - `openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`
  - `openspec/changes/consolidate-lifecycle-recommendation-service/specs/lifecycle-recommendation-service-adapter/spec.md`.
- **Action**: write each file using the corresponding
  template under
  `openspec/schemas/skill-forge-governance/templates/`.
  The `verification.md` is the last artifact and is
  written after the implementation and tests pass.
- **Verification**:
  - Command:
    `ls openspec/changes/consolidate-lifecycle-recommendation-service/`
  - Expected exit code: 0
  - Expected observation: the eight artifact files are
    present.
- **Escalation**: stop and report if any file is
  missing.

### Step 3: Implement the adapter in the service module

- **Files**:
  `src/skill_forge/lifecycle/recommendation.py`.
- **Action**: add a private function
  `_summary_to_input(summary: LifecycleSummary) -> LifecycleRecommendationInput`
  that maps a `LifecycleSummary` to a
  `LifecycleRecommendationInput`. Use a lazy import
  inside the function body to break the circular
  dependency with
  `skill_forge.lifecycle.recommendation_rules`.
  Refactor `LifecycleRecommendationService.recommend`
  to call `recommend_lifecycle_action(_summary_to_input(summary))`.
  Remove the now-redundant
  `_recommend_from_summary` and `_summary_signals`
  private functions. Keep the `compare` method and
  its helpers as-is.
- **Verification**:
  - Command: `python -c "from skill_forge.lifecycle.recommendation import LifecycleRecommendationService; print('ok')"`
  - Expected exit code: 0
  - Expected observation: the import succeeds and
    prints `ok`.
- **Escalation**: stop and report on any
  `ImportError`, `SyntaxError`, or circular-import
  error. If the lazy import is not enough, escalate
  and ask the user.

### Step 4: Add the parity tests

- **Files**:
  `tests/test_lifecycle_recommendation.py`.
- **Action**: add three parity tests that verify the
  service-level `recommend` method matches the pure
  function for the same `LifecycleState` across the
  three required paths (outdated provenance, current
  metadata, unknown/new skill). The parity tests
  assert on the full `model_dump()` of both
  recommendations to guarantee byte-for-byte parity.
- **Verification**:
  - Command:
    `uv run pytest tests/test_lifecycle_recommendation.py -v`
  - Expected exit code: 0
  - Expected observation: every test in the file
    passes, including the three new parity tests.
- **Escalation**: if any test fails, apply
  `systematic-debugging` from `SUPERPOWERS.md`
  (reproduce, locate root cause, fix, do not modify
  the test to match a broken implementation).

### Step 5: Run the full verification suite

- **Files**: none (read-only commands).
- **Action**: run the final verification commands
  listed in the "Final Verification" section below.
- **Verification**:
  - Command: see "Final Verification" below.
  - Expected exit code: 0 for every command.
  - Expected observation: every command succeeds and
    the change is included in the passed list.
- **Escalation**: if any command fails, stop and
  report. Do not paper over the failure.

### Step 6: Write the verification reports

- **Files**:
  - `openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`
  - `docs/00-project/lifecycle-service-adapter-verification-report.md`.
- **Action**: write both files. The change-folder
  `verification.md` records the OpenSpec-level
  evidence record. The docs-level report is a
  human-readable summary written for the Phase 5
  commit.
- **Verification**:
  - Command:
    `cat openspec/changes/consolidate-lifecycle-recommendation-service/verification.md | head -20`
  - Expected exit code: 0
  - Expected observation: the file starts with
    `> Status: draft` and
    `> Schema: skill-forge-governance`.
- **Escalation**: stop and report if the file cannot
  be written.

### Step 7: Commit only Phase 5 files

- **Files**: every file under the allowed-path list
  that actually changed in this phase, plus the new
  files under `docs/00-project/` (the verification
  report).
- **Action**: use explicit `git add <path>` commands
  for each file. Do not use `git add .` or
  `git add -A`. Commit with the message
  `refactor: reuse lifecycle recommendation rules in service`.
- **Verification**:
  - Command: `git show --stat HEAD`
  - Expected exit code: 0
  - Expected observation: the commit's file list
    matches the Phase 5 file list. No pre-existing WIP
    file is included.
- **Escalation**: if `git show --stat HEAD` reports a
  file that is not in the Phase 5 file list, stop and
  report. Do not amend the commit.

## Final Verification

- Command: `git status --short`
- Command: `git diff --name-only`
- Command:
  `openspec validate consolidate-lifecycle-recommendation-service --strict`
- Command: `openspec validate --strict --all`
- Command:
  `uv run pytest tests/test_lifecycle_recommendation_rules.py`
- Command: `uv run pytest tests/test_lifecycle_recommendation.py`
- Command: `uv run pytest`
- Command: `uv run skill-forge --help`
- Command: `python scripts/governance_check.py --quick`
- Command: `python scripts/governance_check.py`

## Rollback

1. Reset the working tree to `HEAD` (do not run
   `git reset --hard` before the commit; if the
   commit has landed, run `git revert HEAD` instead).
2. If the revert is not possible because the commit
   has already been pushed, run `git revert HEAD` and
   push the revert.
3. No data migration. The adapter is in-memory only
   and did not write to disk.
4. If a follow-up change wants to keep any of the new
   OpenSpec artifacts, cherry-pick them individually
   rather than reverting the whole commit.

## Hand-off Note

- The single most important rule for this change is:
  **the public service API must not change**. Every
  test, every artifact, and every commit must respect
  that boundary. The slice is an internal
  adapter/refactor; if a step needs to change the
  service's public surface, stop and report.
