# Tasks: triage-dirty-worktree-change-queue

> Status: draft
> Schema: skill-forge-governance
> Depends on: plan.md
>
> The apply phase parses checkboxes to track progress.
> Tasks not using `- [ ]` will not be tracked. Each
> task must have an observable completion condition and
> cite the file(s) it touches.

## 1. Collect git state

- [ ] 1.1 Run `git status --short` from the repository
  root. Files: none. Observation: the command exits
  0 and lists every modified, deleted, and untracked
  entry in the working tree.
- [ ] 1.2 Run `git diff --name-only` from the
  repository root. Files: none. Observation: the
  command exits 0 and lists the paths of every
  modified tracked file.
- [ ] 1.3 Run `git ls-files --others --exclude-standard`
  from the repository root. Files: none. Observation:
  the command exits 0 and lists every untracked entry
  that is not excluded by `.gitignore`.
- [ ] 1.4 Run `git diff --stat` from the repository
  root. Files: none. Observation: the command exits
  0 and lists the per-file line counts for every
  modified tracked file.
- [ ] 1.5 Run `git log --oneline -10` from the
  repository root. Files: none. Observation: the
  command exits 0 and lists the ten most recent
  commits.

## 2. Create the OpenSpec change skeleton

- [ ] 2.1 Create
  `openspec/changes/triage-dirty-worktree-change-queue/.openspec.yaml`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/.openspec.yaml`.
  Observation: the file's first line is
  `schema: skill-forge-governance` and the file has
  `created:` and `updated:` lines set to today's date
  (`2026-06-06`).
- [ ] 2.2 Write
  `openspec/changes/triage-dirty-worktree-change-queue/brainstorm.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/brainstorm.md`.
  Observation: the file starts with
  `> Status: draft` and `> Schema: skill-forge-governance`,
  and contains the `## Problem`, `## Context`,
  `## Options`, `## Assumptions`, `## Open Questions`,
  and `## Recommendation` sections.
- [ ] 2.3 Write
  `openspec/changes/triage-dirty-worktree-change-queue/proposal.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/proposal.md`.
  Observation: the file starts with
  `> Status: draft` and `> Schema: skill-forge-governance`,
  and contains the `## Why`, `## What Changes`,
  `## Capabilities`, `## Impact`, `## Non-Goals`,
  `## Risks`, `## Rollback`, and
  `## Consistency With Brainstorm` sections.
- [ ] 2.4 Write
  `openspec/changes/triage-dirty-worktree-change-queue/design.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/design.md`.
  Observation: the file starts with
  `> Status: draft` and `> Schema: skill-forge-governance`,
  and contains the `## Context`, `## Goals / Non-Goals`,
  `## Decisions`, `## Data Contracts`,
  `## Module Boundaries`, `## Compatibility Impact`,
  `## Offline and Deterministic Mode`,
  `## Security and Filesystem`,
  `## Risks / Trade-offs`, `## Migration Plan`, and
  `## Open Questions` sections.
- [ ] 2.5 Write
  `openspec/changes/triage-dirty-worktree-change-queue/specs/dirty-worktree-change-queue/spec.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/specs/dirty-worktree-change-queue/spec.md`.
  Observation: the file starts with
  `# Dirty Worktree Change Queue Specification` and
  the `> Status: draft`,
  `> Schema: skill-forge-governance`, `> Capability:`,
  and `> File:` markers, and contains the
  `## Purpose`, `## ADDED Requirements`,
  `## MODIFIED Requirements`, `## REMOVED Requirements`,
  and `## RENAMED Requirements` sections.

## 3. Add the planning artifacts

- [ ] 3.1 Write
  `openspec/changes/triage-dirty-worktree-change-queue/review.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/review.md`.
  Observation: the file exists and contains the
  `## Change Id`, `## Scope Coverage`,
  `## Cross-Artifact Consistency`,
  `## Allowed Path List`, `## Verification Readiness`,
  `## Required Changes`, and `## Verdict` sections,
  with verdict `approve`.
- [ ] 3.2 Write
  `openspec/changes/triage-dirty-worktree-change-queue/plan.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/plan.md`.
  Observation: the file exists and contains the
  `## Change Id`, `## Allowed Paths`,
  `## Forbidden Paths`, `## Pre-Conditions`,
  `## Steps`, `## Final Verification`, `## Rollback`,
  and `## Hand-off Note` sections.
- [ ] 3.3 Write
  `openspec/changes/triage-dirty-worktree-change-queue/tasks.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/tasks.md`.
  Observation: this file exists and contains the
  checkbox-tracked task groups for the change.

## 4. Classify the dirty worktree

- [ ] 4.1 Write
  `docs/00-project/wip-disposition-matrix.md`.
  Files: `docs/00-project/wip-disposition-matrix.md`.
  Observation: the file contains a single markdown
  table with columns
  `Path | Status | Class | Reason | Recommended action`,
  and every dirty entry from
  `git status --short` is present in the table
  classified into exactly one of A/B/C/D/E.
- [ ] 4.2 Write `docs/00-project/change-queue.md`.
  Files: `docs/00-project/change-queue.md`.
  Observation: the file contains a numbered list of
  future OpenSpec change ids, each with a one-line
  description, the blocking dependency, the expected
  effort, and the source buckets (A/B/C/D/E entries)
  that the change will absorb.

## 5. Write the top-level report

- [ ] 5.1 Write
  `docs/00-project/dirty-worktree-triage-report.md`.
  Files:
  `docs/00-project/dirty-worktree-triage-report.md`.
  Observation: the file exists and contains the
  required sections (executive summary, git state
  snapshot, classification summary, change queue
  summary, verification command results, dirty
  worktree handling summary, remaining risks,
  follow-up changes, commit SHA placeholder).

## 6. Final Verification

- [ ] 6.1 Run
  `openspec validate triage-dirty-worktree-change-queue --strict`
  from the repository root. Files: none. Observation:
  the command exits 0 and reports the change as
  `valid`.
- [ ] 6.2 Run `openspec validate --strict --all`
  from the repository root. Files: none. Observation:
  the command exits 0 and the new change is included
  in the passed list.
- [ ] 6.3 Run
  `python scripts/governance_check.py --quick` from
  the repository root. Files: none. Observation: the
  script prints PASS lines for the two quick-mode
  commands and exits 0.
- [ ] 6.4 (Recommended) Run
  `python scripts/governance_check.py` from the
  repository root. Files: none. Observation: the
  script prints PASS lines for the six full-mode
  commands and exits 0.
- [ ] 6.5 (Recommended) Run `uv run pytest` from the
  repository root. Files: none. Observation: the
  full test suite passes.
- [ ] 6.6 (Recommended) Run `uv run skill-forge --help`
  from the repository root. Files: none. Observation:
  the CLI loads; the pre-existing `lifecycle` command
  is unchanged.
- [ ] 6.7 Write
  `openspec/changes/triage-dirty-worktree-change-queue/verification.md`.
  Files:
  `openspec/changes/triage-dirty-worktree-change-queue/verification.md`.
  Observation: the file exists and contains the
  `## Change Id`, `## Executed Commands`,
  `## Test Results`, `## OpenSpec Validation`,
  `## Skipped Commands`, `## Deviations from Plan`,
  `## Remaining Risks`, `## Follow-up Changes`,
  `## Verdict`, and `## Commit SHA` sections.
- [ ] 6.8 Update
  `docs/00-project/dirty-worktree-triage-report.md`
  with the final commit SHA. Files:
  `docs/00-project/dirty-worktree-triage-report.md`.
  Observation: the file's `## Commit SHA` section
  is filled in with the actual short SHA, full SHA,
  and commit message.
- [ ] 6.9 Commit only Phase 6 files using explicit
  `git add <path>` commands for each of the 12
  allowed paths (no `git add .` or `git add -A`).
  Files: the 12 allowed-path groups. Observation:
  the commit's changed file list is exactly the
  12 allowed-path files.
