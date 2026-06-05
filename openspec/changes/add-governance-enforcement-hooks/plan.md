# Plan: add-governance-enforcement-hooks

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, specs/governance-enforcement-hooks/spec.md, design.md, review.md
>
> The plan is the executable contract between the planning
> agent and the implementation agent. It is runnable by a
> weaker agent that has not seen the conversation history.

## Change Id

`add-governance-enforcement-hooks`

## Allowed Paths

- `openspec/changes/add-governance-enforcement-hooks/.openspec.yaml`
- `openspec/changes/add-governance-enforcement-hooks/brainstorm.md`
- `openspec/changes/add-governance-enforcement-hooks/proposal.md`
- `openspec/changes/add-governance-enforcement-hooks/design.md`
- `openspec/changes/add-governance-enforcement-hooks/review.md`
- `openspec/changes/add-governance-enforcement-hooks/plan.md`
- `openspec/changes/add-governance-enforcement-hooks/tasks.md`
- `openspec/changes/add-governance-enforcement-hooks/verification.md`
- `openspec/changes/add-governance-enforcement-hooks/specs/governance-enforcement-hooks/spec.md`
- `scripts/governance_check.py`
- `tests/test_governance_check.py`
- `docs/00-project/governance-enforcement-verification-report.md`

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
- `openspec/changes/add-skill-lifecycle-recommendation/**`
- `templates/**`
- `configs/**`
- `pyproject.toml`
- `uv.lock`
- Every file under `src/**`.
- Every file under `tests/**` that is not
  `tests/test_governance_check.py`.
- Every file under `docs/00-project/**` that is not
  `docs/00-project/governance-enforcement-verification-report.md`.

## Pre-Conditions

- [x] `review.md` verdict is `approve`.
- [x] Working tree may contain pre-existing dirty WIP. The
      implementation must not reset, delete, or include those
      WIP files in the Phase 4 commit. The implementation must
      use explicit `git add <file>` commands and must not use
      `git add .` or `git add -A`.
- [x] The required tools are present: `python`, `git`,
      `openspec` CLI, `uv`, `pytest`.

## Steps

### Step 1: Create the change folder skeleton

- **Files**:
  - `openspec/changes/add-governance-enforcement-hooks/.openspec.yaml`.
- **Action**: create the folder and the `.openspec.yaml`
  with `schema: skill-forge-governance`, `created:` and
  `updated:` lines set to today's date.
- **Verification**:
  - Command: `cat openspec/changes/add-governance-enforcement-hooks/.openspec.yaml`
  - Expected exit code: 0
  - Expected observation: first line is
    `schema: skill-forge-governance`.
- **Escalation**: stop and report if the file cannot be
  written.

### Step 2: Write the eight governance artifacts

- **Files**:
  - `openspec/changes/add-governance-enforcement-hooks/brainstorm.md`
  - `openspec/changes/add-governance-enforcement-hooks/proposal.md`
  - `openspec/changes/add-governance-enforcement-hooks/design.md`
  - `openspec/changes/add-governance-enforcement-hooks/review.md`
  - `openspec/changes/add-governance-enforcement-hooks/plan.md`
  - `openspec/changes/add-governance-enforcement-hooks/tasks.md`
  - `openspec/changes/add-governance-enforcement-hooks/verification.md`
  - `openspec/changes/add-governance-enforcement-hooks/specs/governance-enforcement-hooks/spec.md`.
- **Action**: write each file using the corresponding
  template under
  `openspec/schemas/skill-forge-governance/templates/`. The
  `verification.md` is the last artifact and is written
  after the implementation and tests pass.
- **Verification**:
  - Command: `ls openspec/changes/add-governance-enforcement-hooks/`
  - Expected exit code: 0
  - Expected observation: the eight artifact files are
    present.
- **Escalation**: stop and report if any file is missing.

### Step 3: Create the governance check script

- **Files**: `scripts/governance_check.py`.
- **Action**: create the `scripts/` directory and write
  the script. The script exposes
  `build_command_list(quick: bool) -> list[Command]`,
  `summarize_results(results: list[Result]) -> Summary`,
  `run_command(cmd: list[str], cwd: str) -> Result`, and
  `main(argv: list[str]) -> int`. The script uses only the
  standard library.
- **Verification**:
  - Command: `python scripts/governance_check.py --help`
  - Expected exit code: 0
  - Expected observation: the script prints its `--help`
    text and exits 0.
- **Escalation**: stop and report on any `ImportError` or
  `SyntaxError`.

### Step 4: Create the unit test file

- **Files**: `tests/test_governance_check.py`.
- **Action**: write the unit test file. The tests cover at
  least: full-mode command list, `--quick` command list,
  result aggregation, non-zero exit on required failure,
  skip reporting for a missing optional tool, and a
  no-mutation assertion on the working directory. The
  tests use `monkeypatch` and `unittest.mock` to
  substitute the subprocess runner.
- **Verification**:
  - Command: `uv run pytest tests/test_governance_check.py -v`
  - Expected exit code: 0
  - Expected observation: every test in the new file
    passes.
- **Escalation**: if any test fails, apply
  `systematic-debugging` from `SUPERPOWERS.md` (reproduce,
  locate root cause, fix, do not modify the test to match
  a broken implementation).

### Step 5: Run the full verification suite

- **Files**: none (read-only commands).
- **Action**: run the final verification commands listed
  in the "Final Verification" section below.
- **Verification**:
  - Command: see "Final Verification" below.
  - Expected exit code: 0 for every command except
    `python scripts/governance_check.py` when the gates
    pass; exit code 0 expected there too.
  - Expected observation: every command succeeds and the
    change is included in the passed list.
- **Escalation**: if any command fails, stop and report.
  Do not paper over the failure.

### Step 6: Write the verification reports

- **Files**:
  - `openspec/changes/add-governance-enforcement-hooks/verification.md`
  - `docs/00-project/governance-enforcement-verification-report.md`.
- **Action**: write both files. The change-folder
  `verification.md` records the OpenSpec-level evidence
  record. The docs-level report is a human-readable
  summary written for the Phase 4 commit.
- **Verification**:
  - Command: `cat openspec/changes/add-governance-enforcement-hooks/verification.md | head -20`
  - Expected exit code: 0
  - Expected observation: the file starts with
    `> Status: draft` and `> Schema: skill-forge-governance`.
- **Escalation**: stop and report if the file cannot be
  written.

### Step 7: Commit only Phase 4 files

- **Files**: every file under the allowed-path list that
  actually changed in this phase, plus the new files under
  `docs/00-project/` (the verification report).
- **Action**: use explicit `git add <path>` commands for
  each file. Do not use `git add .` or `git add -A`.
  Commit with the message
  `chore: add governance enforcement check`.
- **Verification**:
  - Command: `git show --stat HEAD`
  - Expected exit code: 0
  - Expected observation: the commit's file list matches
    the Phase 4 file list. No pre-existing WIP file is
    included.
- **Escalation**: if `git show --stat HEAD` reports a file
  that is not in the Phase 4 file list, stop and report.
  Do not amend the commit.

## Final Verification

- Command: `git status --short`
- Command: `git diff --name-only`
- Command: `openspec validate add-governance-enforcement-hooks --strict`
- Command: `openspec validate --strict --all`
- Command: `uv run pytest`
- Command: `uv run pytest tests/test_governance_check.py`
- Command: `uv run skill-forge --help`
- Command: `python scripts/governance_check.py --quick`
- Command: `python scripts/governance_check.py`

## Rollback

1. Reset the working tree to `HEAD` (do not run
   `git reset --hard` before the commit; if the commit
   has landed, run `git revert HEAD` instead).
2. If the revert is not possible because the commit has
   already been pushed, run `git revert HEAD` and push
   the revert.
3. No data migration. The script is read-only and did
   not write to disk.
4. If a follow-up change wants to keep any of the new
   OpenSpec artifacts, cherry-pick them individually
   rather than reverting the whole commit.

## Hand-off Note

- The single most important rule for this change is:
  **the script must not modify the repository**. Every
  test, every artifact, and every commit must respect
  that boundary. If a step needs to write a file, stop
  and report; the script is a reporter, not a writer.
