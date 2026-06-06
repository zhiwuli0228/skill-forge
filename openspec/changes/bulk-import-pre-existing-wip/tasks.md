# Tasks: bulk-import-pre-existing-wip

> Status: draft
> Schema: skill-forge-governance
> Depends on: plan.md
>
> The apply phase parses checkboxes to track progress.
> Tasks not using `- [ ]` will not be tracked. Each
> task must have an observable completion condition and
> cite the file(s) it touches.

## 1. Create the OpenSpec change skeleton

- [ ] 1.1 Create
  `openspec/changes/bulk-import-pre-existing-wip/.openspec.yaml`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/.openspec.yaml`.
  Observation: the file's first line is
  `schema: skill-forge-governance` and the file has
  `created:` and `updated:` lines set to today's date
  (`2026-06-06`).
- [ ] 1.2 Write
  `openspec/changes/bulk-import-pre-existing-wip/brainstorm.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/brainstorm.md`.
  Observation: the file starts with
  `> Status: draft` and `> Schema: skill-forge-governance`,
  and contains the `## Problem`, `## Context`,
  `## Options`, `## Assumptions`, `## Open Questions`,
  and `## Recommendation` sections.
- [ ] 1.3 Write
  `openspec/changes/bulk-import-pre-existing-wip/proposal.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/proposal.md`.
  Observation: the file starts with
  `> Status: draft` and `> Schema: skill-forge-governance`,
  and contains the `## Why`, `## What Changes`,
  `## Capabilities`, `## Impact`, `## Non-Goals`,
  `## Risks`, `## Rollback`, and
  `## Consistency With Brainstorm` sections.
- [ ] 1.4 Write
  `openspec/changes/bulk-import-pre-existing-wip/design.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/design.md`.
  Observation: the file starts with
  `> Status: draft` and `> Schema: skill-forge-governance`,
  and contains the `## Context`, `## Goals / Non-Goals`,
  `## Decisions`, `## Data Contracts`,
  `## Module Boundaries`, `## Compatibility Impact`,
  `## Offline and Deterministic Mode`,
  `## Security and Filesystem`,
  `## Risks / Trade-offs`, `## Migration Plan`, and
  `## Open Questions` sections.
- [ ] 1.5 Write
  `openspec/changes/bulk-import-pre-existing-wip/specs/pre-existing-wip-bulk-import/spec.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/specs/pre-existing-wip-bulk-import/spec.md`.
  Observation: the file starts with
  `# Pre-Existing WIP Bulk Import Specification` and
  the `> Status: draft`,
  `> Schema: skill-forge-governance`, `> Capability:`,
  and `> File:` markers, and contains the
  `## Purpose`, `## ADDED Requirements`,
  `## MODIFIED Requirements`, `## REMOVED Requirements`,
  and `## RENAMED Requirements` sections.

## 2. Add the planning artifacts

- [ ] 2.1 Write
  `openspec/changes/bulk-import-pre-existing-wip/review.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/review.md`.
  Observation: the file exists and contains the
  `## Change Id`, `## Scope Coverage`,
  `## Cross-Artifact Consistency`,
  `## Allowed Path List`, `## Verification Readiness`,
  `## Required Changes`, and `## Verdict` sections,
  with verdict `approve`.
- [ ] 2.2 Write
  `openspec/changes/bulk-import-pre-existing-wip/plan.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/plan.md`.
  Observation: the file exists and contains the
  `## Change Id`, `## Allowed Paths`,
  `## Forbidden Paths`, `## Pre-Conditions`,
  `## Steps`, `## Final Verification`, `## Rollback`,
  and `## Hand-off Note` sections.
- [ ] 2.3 Write
  `openspec/changes/bulk-import-pre-existing-wip/tasks.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/tasks.md`.
  Observation: this file exists and contains the
  checkbox-tracked task groups for the change.

## 3. Update the Phase 6 docs

- [ ] 3.1 Update
  `docs/00-project/wip-disposition-matrix.md`.
  Files:
  `docs/00-project/wip-disposition-matrix.md`.
  Observation: the file has a "Phase 7 Bulk Slice"
  section that marks the absorbed entries as
  "absorbed by `bulk-import-pre-existing-wip`" and
  the deferred D + E entries as "deferred to
  future phase".
- [ ] 3.2 Update
  `docs/00-project/change-queue.md`.
  Files: `docs/00-project/change-queue.md`.
  Observation: the file has a "Status" or
  "Absorbed by" annotation per absorbed future
  change, and a "Deferred entries" section for the
  D + E classes.
- [ ] 3.3 Update
  `docs/00-project/dirty-worktree-triage-report.md`.
  Files:
  `docs/00-project/dirty-worktree-triage-report.md`.
  Observation: the file has a "Phase 7 Bulk Slice"
  section that records the commit SHA, the
  deferred D + E entries, and the push
  confirmation.

## 4. Stage the A + B entries

- [ ] 4.1 Stage the 7 A-class deletions under
  `openspec/changes/add-community-skill-discovery/`
  with `git rm` (or `git add` for tracked deletions).
  Files: the 7 specific files listed in
  `review.md`.
  Observation: `git diff --cached --stat` shows the
  7 deletions in the staged set.
- [ ] 4.2 Stage the 11 A-class archive folders
  with `git add <folder>/`. Files: the 11 archive
  folders listed in `review.md`.
  Observation: `git diff --cached --stat` shows the
  11 archive folders in the staged set.
- [ ] 4.3 Stage the 21 B-class modified tracked
  files with `git add <path>`. Files: the 21
  modified tracked files listed in `review.md`.
  Observation: `git diff --cached --stat` shows the
  21 modified files in the staged set.
- [ ] 4.4 Stage the 21 B-class untracked files
  with `git add <path>`. Files: the 21 untracked
  files listed in `review.md`.
  Observation: `git diff --cached --stat` shows the
  21 untracked files in the staged set.
- [ ] 4.5 Verify the staged set: the staged set
  contains exactly the A + B paths; no D + E paths;
  no forbidden paths; no duplicate spec. Files:
  none. Observation: `git diff --cached --name-only`
  shows the expected list; `git status --short`
  shows the untracked D + E entries as `??` and the
  duplicate spec as `??` (not staged).

## 5. Final Verification

- [ ] 5.1 Run
  `openspec validate bulk-import-pre-existing-wip --strict`
  from the repository root. Files: none.
  Observation: the command exits 0 and reports the
  change as `valid`.
- [ ] 5.2 Run `openspec validate --strict --all`
  from the repository root. Files: none.
  Observation: the command exits 0 and the new
  change is included in the passed list.
- [ ] 5.3 Run
  `python scripts/governance_check.py --quick` from
  the repository root. Files: none. Observation: the
  script prints PASS lines for the two quick-mode
  commands and exits 0.
- [ ] 5.4 Run
  `python scripts/governance_check.py` from the
  repository root. Files: none. Observation: the
  script prints PASS lines for the six full-mode
  commands and exits 0.
- [ ] 5.5 Run `uv run pytest` from the repository
  root. Files: none. Observation: the full test
  suite passes (310+ tests; the dirty-worktree
  additions may add new tests, so the count may
  exceed 310).
- [ ] 5.6 Run `uv run skill-forge --help` from the
  repository root. Files: none. Observation: the
  CLI loads; the pre-existing `lifecycle` command
  is unchanged.
- [ ] 5.7 Write
  `openspec/changes/bulk-import-pre-existing-wip/verification.md`.
  Files:
  `openspec/changes/bulk-import-pre-existing-wip/verification.md`.
  Observation: the file exists and contains the
  `## Change Id`, `## Executed Commands`,
  `## Test Results`, `## OpenSpec Validation`,
  `## Skipped Commands`, `## Deviations from Plan`,
  `## Remaining Risks`, `## Follow-up Changes`,
  `## Verdict`, and `## Commit SHA` sections.
- [ ] 5.8 Write
  `docs/00-project/bulk-import-verification-report.md`.
  Files:
  `docs/00-project/bulk-import-verification-report.md`.
  Observation: the file exists and contains the
  required sections (executive summary, git state
  snapshot, classification summary, change queue
  summary, verification command results, dirty
  worktree handling summary, remaining risks,
  follow-up changes, commit SHA placeholder).

## 6. Commit and push

- [ ] 6.1 Commit the staged set with the message
  `docs: bulk import pre-existing wip`. Files: the
  staged set. Observation: the commit's changed
  file list is exactly the A + B paths.
- [ ] 6.2 Update the verification.md and the
  bulk-import-verification-report.md with the
  actual commit SHA. Files: the 2 verification
  files. Observation: the files' `## Commit SHA`
  sections are filled in with the actual short
  SHA, full SHA, and commit message.
- [ ] 6.3 Commit the verification updates with
  the message
  `docs: record Phase 7 commit SHA in verification
  report`. Files: the 2 verification files.
  Observation: the follow-up docs commit changes
  only the 2 files.
- [ ] 6.4 Push both commits to `origin/main` with
  `git push origin main`. Files: none.
  Observation: `git log --oneline origin/main -2`
  shows the bulk-slice commit and the follow-up
  docs commit at the top of `origin/main`.
