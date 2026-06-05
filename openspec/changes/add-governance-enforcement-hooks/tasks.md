# Tasks: add-governance-enforcement-hooks

> Status: draft
> Schema: skill-forge-governance
> Depends on: plan.md
>
> The apply phase parses checkboxes to track progress. Tasks
> not using `- [ ]` will not be tracked. Each task must have
> an observable completion condition and cite the file(s) it
> touches.

## 1. Create the OpenSpec change skeleton

- [ ] 1.1 Create `openspec/changes/add-governance-enforcement-hooks/.openspec.yaml`. Files: `openspec/changes/add-governance-enforcement-hooks/.openspec.yaml`. Observation: the file's first line is `schema: skill-forge-governance` and the file has `created:` and `updated:` lines set to today's date.
- [ ] 1.2 Write `openspec/changes/add-governance-enforcement-hooks/brainstorm.md`. Files: `openspec/changes/add-governance-enforcement-hooks/brainstorm.md`. Observation: the file exists, starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Problem`, `## Context`, `## Options`, `## Assumptions`, `## Open Questions`, and `## Recommendation` sections.
- [ ] 1.3 Write `openspec/changes/add-governance-enforcement-hooks/proposal.md`. Files: `openspec/changes/add-governance-enforcement-hooks/proposal.md`. Observation: the file starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Why`, `## What Changes`, `## Capabilities`, `## Impact`, `## Non-Goals`, `## Risks`, `## Rollback`, and `## Consistency With Brainstorm` sections.
- [ ] 1.4 Write `openspec/changes/add-governance-enforcement-hooks/design.md`. Files: `openspec/changes/add-governance-enforcement-hooks/design.md`. Observation: the file starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Context`, `## Goals / Non-Goals`, `## Decisions`, `## Data Contracts`, `## Module Boundaries`, `## Compatibility Impact`, `## Offline and Deterministic Mode`, `## Security and Filesystem`, `## Risks / Trade-offs`, `## Migration Plan`, and `## Open Questions` sections.
- [ ] 1.5 Write `openspec/changes/add-governance-enforcement-hooks/specs/governance-enforcement-hooks/spec.md`. Files: `openspec/changes/add-governance-enforcement-hooks/specs/governance-enforcement-hooks/spec.md`. Observation: the file starts with `# Governance Enforcement Hooks Specification` and the `> Status: draft`, `> Schema: skill-forge-governance`, `> Capability:`, and `> File:` markers, and contains the `## Purpose`, `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, and `## RENAMED Requirements` sections.

## 2. Add the planning artifacts

- [ ] 2.1 Write `openspec/changes/add-governance-enforcement-hooks/review.md`. Files: `openspec/changes/add-governance-enforcement-hooks/review.md`. Observation: the file exists and contains the `## Change Id`, `## Scope Coverage`, `## Cross-Artifact Consistency`, `## Allowed Path List`, `## Verification Readiness`, and `## Verdict` sections, with verdict `approve`.
- [ ] 2.2 Write `openspec/changes/add-governance-enforcement-hooks/plan.md`. Files: `openspec/changes/add-governance-enforcement-hooks/plan.md`. Observation: the file exists and contains the `## Change Id`, `## Allowed Paths`, `## Forbidden Paths`, `## Pre-Conditions`, `## Steps`, `## Final Verification`, and `## Rollback` sections.
- [ ] 2.3 Write `openspec/changes/add-governance-enforcement-hooks/tasks.md`. Files: `openspec/changes/add-governance-enforcement-hooks/tasks.md`. Observation: the file exists and contains the checkbox-tracked task groups for the change.

## 3. Implement the governance check script

- [ ] 3.1 Create `scripts/governance_check.py`. Files: `scripts/governance_check.py`. Observation: the file exists, imports only standard-library modules, and exposes `build_command_list(quick: bool) -> list[Command]`, `summarize_results(results: list[Result]) -> Summary`, `run_command(cmd: list[str], cwd: str) -> Result`, and `main(argv: list[str]) -> int`.
- [ ] 3.2 Create `tests/test_governance_check.py`. Files: `tests/test_governance_check.py`. Observation: the file exists and contains at least six tests covering full-mode command list, `--quick` command list, result aggregation, non-zero exit on required failure, skip reporting for a missing optional tool, and no repository mutation. The tests use `monkeypatch` and `unittest.mock` to substitute the subprocess runner.

## 4. Final Verification

- [ ] 4.1 Run `git status --short` from the repository root. Files: none. Observation: only files under `openspec/changes/add-governance-enforcement-hooks/`, the new `scripts/governance_check.py`, the new `tests/test_governance_check.py`, and the new `docs/00-project/governance-enforcement-verification-report.md` are listed (plus any pre-existing WIP that is out of scope).
- [ ] 4.2 Run `git diff --name-only` from the repository root. Files: none. Observation: only the pre-existing dirty WIP paths are listed; the Phase 4 files are untracked and therefore do not appear.
- [ ] 4.3 Run `openspec validate add-governance-enforcement-hooks --strict`. Files: none. Observation: the command exits 0 and reports the change as `valid`.
- [ ] 4.4 Run `openspec validate --strict --all`. Files: none. Observation: the command exits 0 and the new change is included in the passed list.
- [ ] 4.5 Run `uv run pytest`. Files: none. Observation: the full test suite passes (280+ tests).
- [ ] 4.6 Run `uv run pytest tests/test_governance_check.py`. Files: none. Observation: the new test file passes.
- [ ] 4.7 Run `uv run skill-forge --help`. Files: none. Observation: the CLI loads; no command is added by this slice.
- [ ] 4.8 Run `python scripts/governance_check.py --quick`. Files: none. Observation: the script prints PASS lines for the two quick-mode commands and exits 0.
- [ ] 4.9 Run `python scripts/governance_check.py`. Files: none. Observation: the script prints PASS lines for the six full-mode commands and exits 0.
- [ ] 4.10 Write `openspec/changes/add-governance-enforcement-hooks/verification.md`. Files: `openspec/changes/add-governance-enforcement-hooks/verification.md`. Observation: the file exists and contains the `## Change Id`, `## Executed Commands`, `## Test Results`, `## OpenSpec Validation`, `## Skipped Commands`, `## Deviations from Plan`, `## Remaining Risks`, `## Follow-up Changes`, and `## Verdict` sections.
- [ ] 4.11 Write `docs/00-project/governance-enforcement-verification-report.md`. Files: `docs/00-project/governance-enforcement-verification-report.md`. Observation: the file exists and contains the required sections (changed files, restricted path check, dirty worktree handling, OpenSpec change summary, script summary, test summary, verification command results, quick/full governance check results, skipped commands and reasons, remaining risks, recommended Phase 5).
- [ ] 4.12 Commit only Phase 4 files using explicit `git add <path>` commands (no `git add .`). Files: the four allowed-path groups. Observation: the commit's changed file list is exactly the Phase 4 file list above.
