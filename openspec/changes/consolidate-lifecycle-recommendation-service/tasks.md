# Tasks: consolidate-lifecycle-recommendation-service

> Status: draft
> Schema: skill-forge-governance
> Depends on: plan.md
>
> The apply phase parses checkboxes to track progress.
> Tasks not using `- [ ]` will not be tracked. Each task
> must have an observable completion condition and cite
> the file(s) it touches.

## 1. Create the OpenSpec change skeleton

- [ ] 1.1 Create `openspec/changes/consolidate-lifecycle-recommendation-service/.openspec.yaml`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/.openspec.yaml`. Observation: the file's first line is `schema: skill-forge-governance` and the file has `created:` and `updated:` lines set to today's date.
- [ ] 1.2 Write `openspec/changes/consolidate-lifecycle-recommendation-service/brainstorm.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/brainstorm.md`. Observation: the file exists, starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Problem`, `## Context`, `## Options`, `## Assumptions`, `## Open Questions`, and `## Recommendation` sections.
- [ ] 1.3 Write `openspec/changes/consolidate-lifecycle-recommendation-service/proposal.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/proposal.md`. Observation: the file starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Why`, `## What Changes`, `## Capabilities`, `## Impact`, `## Non-Goals`, `## Risks`, `## Rollback`, and `## Consistency With Brainstorm` sections.
- [ ] 1.4 Write `openspec/changes/consolidate-lifecycle-recommendation-service/design.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/design.md`. Observation: the file starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Context`, `## Goals / Non-Goals`, `## Decisions`, `## Data Contracts`, `## Module Boundaries`, `## Compatibility Impact`, `## Offline and Deterministic Mode`, `## Security and Filesystem`, `## Risks / Trade-offs`, `## Migration Plan`, and `## Open Questions` sections.
- [ ] 1.5 Write `openspec/changes/consolidate-lifecycle-recommendation-service/specs/lifecycle-recommendation-service-adapter/spec.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/specs/lifecycle-recommendation-service-adapter/spec.md`. Observation: the file starts with `# Lifecycle Recommendation Service Adapter Specification` and the `> Status: draft`, `> Schema: skill-forge-governance`, `> Capability:`, and `> File:` markers, and contains the `## Purpose`, `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, and `## RENAMED Requirements` sections.

## 2. Add the planning artifacts

- [ ] 2.1 Write `openspec/changes/consolidate-lifecycle-recommendation-service/review.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/review.md`. Observation: the file exists and contains the `## Change Id`, `## Scope Coverage`, `## Cross-Artifact Consistency`, `## Allowed Path List`, `## Verification Readiness`, and `## Verdict` sections, with verdict `approve`.
- [ ] 2.2 Write `openspec/changes/consolidate-lifecycle-recommendation-service/plan.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/plan.md`. Observation: the file exists and contains the `## Change Id`, `## Allowed Paths`, `## Forbidden Paths`, `## Pre-Conditions`, `## Steps`, `## Final Verification`, and `## Rollback` sections.
- [ ] 2.3 Write `openspec/changes/consolidate-lifecycle-recommendation-service/tasks.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/tasks.md`. Observation: the file exists and contains the checkbox-tracked task groups for the change.

## 3. Implement the adapter

- [ ] 3.1 Refactor `src/skill_forge/lifecycle/recommendation.py`. Files: `src/skill_forge/lifecycle/recommendation.py`. Observation: the file adds a private `_summary_to_input` function (with a lazy import of `LifecycleRecommendationInput` and `recommend_lifecycle_action` inside the function body), modifies `LifecycleRecommendationService.recommend` to call `recommend_lifecycle_action(_summary_to_input(summary))`, and removes the now-redundant `_recommend_from_summary` and `_summary_signals` private functions. The `compare` method, `_comparison_key`, `_compare_reason`, and `_tie_breaker_reason` are preserved.
- [ ] 3.2 Add parity tests to `tests/test_lifecycle_recommendation.py`. Files: `tests/test_lifecycle_recommendation.py`. Observation: the file contains at least the three required parity tests (`test_service_outdated_provenance_matches_pure_function`, `test_service_current_metadata_matches_pure_function`, `test_service_unknown_new_skill_matches_pure_function`) and the pre-existing tests in the file are preserved.

## 4. Final Verification

- [ ] 4.1 Run `git status --short` from the repository root. Files: none. Observation: only files under `openspec/changes/consolidate-lifecycle-recommendation-service/`, the modified `src/skill_forge/lifecycle/recommendation.py`, the modified `tests/test_lifecycle_recommendation.py`, and the new `docs/00-project/lifecycle-service-adapter-verification-report.md` are listed (plus any pre-existing WIP that is out of scope).
- [ ] 4.2 Run `git diff --name-only` from the repository root. Files: none. Observation: only the pre-existing dirty WIP paths are listed; the Phase 5 files are untracked or modified, and the modified ones are the allowed-path files only.
- [ ] 4.3 Run `openspec validate consolidate-lifecycle-recommendation-service --strict`. Files: none. Observation: the command exits 0 and reports the change as `valid`.
- [ ] 4.4 Run `openspec validate --strict --all`. Files: none. Observation: the command exits 0 and the new change is included in the passed list.
- [ ] 4.5 Run `uv run pytest tests/test_lifecycle_recommendation_rules.py`. Files: none. Observation: the pure-function tests pass; the pre-existing tests in `tests/test_lifecycle_recommendation_rules.py` are preserved.
- [ ] 4.6 Run `uv run pytest tests/test_lifecycle_recommendation.py`. Files: none. Observation: the service-level tests pass, including the three new parity tests.
- [ ] 4.7 Run `uv run pytest`. Files: none. Observation: the full test suite passes (304+ tests).
- [ ] 4.8 Run `uv run skill-forge --help`. Files: none. Observation: the CLI loads; the pre-existing `lifecycle` command is unchanged.
- [ ] 4.9 Run `python scripts/governance_check.py --quick`. Files: none. Observation: the script prints PASS lines for the two quick-mode commands and exits 0.
- [ ] 4.10 Run `python scripts/governance_check.py`. Files: none. Observation: the script prints PASS lines for the six full-mode commands and exits 0.
- [ ] 4.11 Write `openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`. Files: `openspec/changes/consolidate-lifecycle-recommendation-service/verification.md`. Observation: the file exists and contains the `## Change Id`, `## Executed Commands`, `## Test Results`, `## OpenSpec Validation`, `## Skipped Commands`, `## Deviations from Plan`, `## Remaining Risks`, `## Follow-up Changes`, and `## Verdict` sections.
- [ ] 4.12 Write `docs/00-project/lifecycle-service-adapter-verification-report.md`. Files: `docs/00-project/lifecycle-service-adapter-verification-report.md`. Observation: the file exists and contains the required sections (changed files, restricted path check, dirty worktree handling, OpenSpec change summary, adapter strategy, parity tests summary, verification command results, quick/full governance check results, skipped commands and reasons, remaining risks).
- [ ] 4.13 Commit only Phase 5 files using explicit `git add <path>` commands (no `git add .`). Files: the four allowed-path groups. Observation: the commit's changed file list is exactly the Phase 5 file list above.
