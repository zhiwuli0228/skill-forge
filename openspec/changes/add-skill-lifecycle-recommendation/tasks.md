# Tasks: add-skill-lifecycle-recommendation

> Status: draft
> Schema: skill-forge-governance
> Depends on: plan.md
>
> The apply phase parses checkboxes to track progress. Tasks
> not using `- [ ]` are not tracked. Each task must cite the
> file(s) it touches and the expected completion observation.

## 1. Reshape the change folder to the eight-artifact structure

- [ ] 1.1 Update `openspec/changes/add-skill-lifecycle-recommendation/.openspec.yaml` so that `schema` is `skill-forge-governance`. Observation: the file's first line is `schema: skill-forge-governance`.
- [ ] 1.2 Write `openspec/changes/add-skill-lifecycle-recommendation/brainstorm.md`. Observation: the file exists, starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Problem`, `## Context`, `## Options`, `## Assumptions`, `## Open Questions`, and `## Recommendation` sections.
- [ ] 1.3 Reshape `openspec/changes/add-skill-lifecycle-recommendation/proposal.md` to the new template. Observation: the file starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Why`, `## What Changes`, `## Capabilities`, `## Impact`, `## Non-Goals`, `## Risks`, `## Rollback`, and `## Consistency With Brainstorm` sections.
- [ ] 1.4 Reshape `openspec/changes/add-skill-lifecycle-recommendation/design.md` to the new template. Observation: the file starts with `> Status: draft` and `> Schema: skill-forge-governance`, and contains the `## Context`, `## Goals / Non-Goals`, `## Decisions`, `## Data Contracts`, `## Module Boundaries`, `## Compatibility Impact`, `## Offline and Deterministic Mode`, `## Security and Filesystem`, `## Risks / Trade-offs`, `## Migration Plan`, and `## Open Questions` sections.

## 2. Reshape the spec file to the new template

- [ ] 2.1 Reshape `openspec/changes/add-skill-lifecycle-recommendation/specs/skill-lifecycle-recommendation/spec.md` to the new template. Observation: the file starts with `# Skill Lifecycle Recommendation Specification` and the `> Status: draft`, `> Schema: skill-forge-governance`, `> Capability:`, and `> File:` markers, and contains the `## Purpose`, `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, and `## RENAMED Requirements` sections.

## 3. Add the missing planning artifacts

- [ ] 3.1 Write `openspec/changes/add-skill-lifecycle-recommendation/review.md`. Observation: the file exists and contains the `## Change Id`, `## Scope Coverage`, `## Cross-Artifact Consistency`, `## Allowed Path List`, `## Verification Readiness`, and `## Verdict` sections, with verdict `approve`.
- [ ] 3.2 Write `openspec/changes/add-skill-lifecycle-recommendation/plan.md`. Observation: the file exists and contains the `## Change Id`, `## Allowed Paths`, `## Forbidden Paths`, `## Pre-Conditions`, `## Steps`, `## Final Verification`, and `## Rollback` sections.
- [ ] 3.3 Write `openspec/changes/add-skill-lifecycle-recommendation/verification.md` (after the implementation and tests are complete). Observation: the file exists and contains the `## Change Id`, `## Executed Commands`, `## Test Results`, `## OpenSpec Validation`, `## Skipped Commands`, `## Deviations from Plan`, `## Remaining Risks`, `## Follow-up Changes`, and `## Verdict` sections.

## 4. Implement the minimal slice

- [ ] 4.1 Add `src/skill_forge/lifecycle/recommendation_rules.py` with the `LifecycleRecommendationInput` Pydantic model and the pure `recommend_lifecycle_action` function. Observation: the file exists, defines the input model with `extra="forbid"`, defines a module-level pure function, and imports the existing `LifecycleRecommendation` and `LifecycleState` from `skill_forge.lifecycle.recommendation` and `skill_forge.lifecycle.models`.
- [ ] 4.2 Add `tests/test_lifecycle_recommendation_rules.py` with unit tests for the pure function. Observation: the file exists and contains at least the five required test cases (unknown state, outdated provenance, current valid metadata, invalid or incomplete input, deterministic behavior).

## 5. Final Verification

- [ ] 5.1 Run `git status --short` from the repository root. Observation: only files under `openspec/changes/add-skill-lifecycle-recommendation/`, the new `src/skill_forge/lifecycle/recommendation_rules.py`, the new `tests/test_lifecycle_recommendation_rules.py`, and the new `docs/00-project/first-governed-change-verification-report.md` are listed (plus any pre-existing WIP that is out of scope).
- [ ] 5.2 Run `openspec validate add-skill-lifecycle-recommendation --strict`. Observation: the command exits 0 and reports the change as `valid`.
- [ ] 5.3 Run `openspec validate --strict --all`. Observation: the command exits 0 and the change is included in the passed list.
- [ ] 5.4 Run `uv run pytest`. Observation: the full test suite passes (265+ tests).
- [ ] 5.5 Run `uv run pytest tests/test_lifecycle_recommendation_rules.py`. Observation: the new test file passes.
- [ ] 5.6 Run `uv run skill-forge --help`. Observation: the CLI loads; pre-existing commands are unchanged.
- [ ] 5.7 Write `docs/00-project/first-governed-change-verification-report.md`. Observation: the file exists and contains the required sections (selected slice, modified files, forbidden-path check, dirty worktree handling, OpenSpec artifact summary, code summary, test summary, verification results, remaining risks, recommended Phase 4).
- [ ] 5.8 Commit only Phase 3 files using explicit `git add` commands (no `git add .`). Observation: the commit's changed file list is exactly the Phase 3 file list above.
