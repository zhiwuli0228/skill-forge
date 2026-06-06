# Docs Classification Plan

> Status: draft
> Date: 2026-06-06
> Companion to: `docs/README.md` and the directory skeleton under `docs/`
>
> This plan classifies every scattered root-level document under `docs/`
> and the documents under `docs/rectification/`. It does not move, delete,
> or rewrite any existing document. It is the input to a future Batch 1
> safe-move change.

## Purpose

The Skill Forge documentation skeleton (`docs/01-architecture/`,
`docs/02-harness/`, `docs/05-development/`, `docs/06-domain/`,
`docs/07-operations/`, `docs/99-archive/`, plus the top-level
`docs/README.md`) is in place, and the first batch of current-authority
docs has been added. The next task is to clean up the scattered
root-level documents that pre-date the skeleton. This plan classifies
those documents, names the recommended destination, and groups the
moves into batches that can be executed safely.

## Current Docs Root Inventory

The table covers every `docs/*.md` file that is not `docs/README.md`,
plus the seven `docs/rectification/*.md` files. `docs/README.md` is the
docs navigation file; it is current authority and stays at the root.

| File | Current Role | Recommended Destination | Classification | Reason | Move Now? | Requires User Decision? |
|---|---|---|---|---|---|---|
| `docs/openspec_change_plan.md` | Historical OpenSpec change-splitting plan and progress tracker. | `docs/99-archive/old-designs/` | Superseded by new authority docs | The change-splitting it tracked is now realized and archived; the active change workflow is in `docs/03-openspec/change-workflow.md`. | yes | no |
| `docs/skill_forge_design_doc.md` | Original product / architecture design doc (Chinese). | `docs/99-archive/old-designs/` (with the option to summarize into `docs/01-architecture/` later) | Architecture source material | Most of its content predates the current architecture; the current architecture authority is in `docs/01-architecture/architecture-overview.md`, `module-boundaries.md`, and `data-flow.md`. | summarize then archive | no |
| `docs/skill_lifecycle_governance_plan.md` | Upstream plan for the lifecycle changes (Chinese). | `docs/99-archive/superseded-roadmaps/` (the lifecycle authority itself lives in `docs/06-domain/lifecycle-rules.md`) | Domain source material | The three changes it proposed were adopted; the current lifecycle authority is `docs/06-domain/lifecycle-rules.md`. | summarize then archive | no |
| `docs/skill_forge_next_evolution_plan.md` | Upstream design for the next-stage capabilities (Chinese). | `docs/00-project/` (after user approval) or `docs/99-archive/superseded-roadmaps/` (if the user prefers) | Planning / backlog | It is a process tracker for future changes, not current authority. The next-step change queue lives in `docs/00-project/change-queue.md`. | no | yes |
| `docs/skill_generation_roadmap.md` | Upstream roadmap for fast-generation capabilities (Chinese). | `docs/00-project/` (after user approval) or `docs/99-archive/superseded-roadmaps/` | Planning / backlog | It is a process tracker, not current authority. | no | yes |
| `docs/intelligent-generation-design.md` | V1 design doc for the intelligent generation capability. | `docs/99-archive/old-designs/` | Superseded by new authority docs | V1 was superseded by `docs/intelligent-generation-design-v2.md` per the V2 doc's own assessment. | yes | no |
| `docs/intelligent-generation-design-v2.md` | V2 design doc for the intelligent generation capability. | `docs/00-project/` (as a deferred roadmap input for the future `add-intelligent-generation-fallback` change) or `docs/99-archive/` | Requires user decision | It is a deferred design input; its destination depends on the user's intent for the future change. | no | yes |
| `docs/intelligent-generation-roadmap.md` | Roadmap for the intelligent generation capability. | `docs/00-project/` (as a deferred roadmap input) or `docs/99-archive/superseded-roadmaps/` | Requires user decision | It is a deferred roadmap input. | no | yes |
| `docs/release-notes.md` | Unreleased release notes draft. | `docs/00-project/release-notes.md` (as the canonical location) or `docs/99-archive/reports/` | Requires user decision | The doc contains unreleased change claims that may or may not be accurate against `main`. The user should confirm the destination and the content. | no | yes |
| `docs/rectification/skill-forge-phase-0-governance-entry-taskbook.md` | Phase 0 taskbook. | `docs/99-archive/taskbooks/` | Process-only | Phase 0 is done; the taskbook is a process artifact, not current authority. | yes | no |
| `docs/rectification/skill-forge-phase-1-openspec-superspec-schema-taskbook.md` | Phase 1 taskbook. | `docs/99-archive/taskbooks/` | Process-only | Phase 1 is done; the taskbook is a process artifact. | yes | no |
| `docs/rectification/skill-forge-phase-2-superpowers-integration-taskbook.md` | Phase 2 taskbook. | `docs/99-archive/taskbooks/` | Process-only | Phase 2 is done; the taskbook is a process artifact. | yes | no |
| `docs/rectification/skill-forge-phase-3-first-real-governed-change-taskbook.md` | Phase 3 taskbook. | `docs/99-archive/taskbooks/` | Process-only | Phase 3 is done; the taskbook is a process artifact. | yes | no |
| `docs/rectification/skill-forge-phase-4-governance-enforcement-hooks-taskbook.md` | Phase 4 taskbook. | `docs/99-archive/taskbooks/` | Process-only | Phase 4 is done; the taskbook is a process artifact. | yes | no |
| `docs/rectification/skill-forge-phase-5-lifecycle-service-adapter-taskbook.md` | Phase 5 taskbook. | `docs/99-archive/taskbooks/` | Process-only | Phase 5 is done; the taskbook is a process artifact. | yes | no |
| `docs/rectification/skill-forge-phase-6-dirty-worktree-triage-taskbook.md` | Phase 6 taskbook. | `docs/99-archive/taskbooks/` | Process-only | Phase 6 is done; the taskbook is a process artifact. | yes | no |

### Notes on the inventory

- **No file is in `docs/01-architecture/`, `docs/02-harness/`,
  `docs/05-development/`, or `docs/06-domain/` from the existing
  scattered set.** The current-authority docs added by the previous
  task are the only entries in those folders.
- **`docs/03-openspec/` and `docs/04-superpowers/` are already
  populated** with current authority docs and are not in this
  inventory.
- **`docs/00-project/` already contains the recommended-file list
  (status, roadmap, reports, change queue).** The recommended
  destinations for the E-class entries below intentionally point
  back to `docs/00-project/` so the queue remains the single source
  of truth for the user.
- **`docs/99-archive/` currently has only `README.md`.** The
  recommended subdirectories (`old-designs/`, `taskbooks/`,
  `reports/`, `superseded-roadmaps/`) are listed in
  `docs/99-archive/README.md` and will be created as part of
  Batch 1.

## Recommended Migration Batches

The migration is split into three batches. Each batch is a separate
follow-up task with its own OpenSpec change (or, for the smallest
batch, a single docs-only change) and its own allowed-path list.

### Batch 1: safe moves

These moves are mechanical and do not require summarization. Every
file in Batch 1 is a process-only artifact or a clearly superseded
historical document. The destination is unambiguous.

- `docs/openspec_change_plan.md` -> `docs/99-archive/old-designs/openspec_change_plan.md`
- `docs/intelligent-generation-design.md` -> `docs/99-archive/old-designs/intelligent-generation-design.md`
- `docs/rectification/skill-forge-phase-0-governance-entry-taskbook.md` -> `docs/99-archive/taskbooks/skill-forge-phase-0-governance-entry-taskbook.md`
- `docs/rectification/skill-forge-phase-1-openspec-superspec-schema-taskbook.md` -> `docs/99-archive/taskbooks/skill-forge-phase-1-openspec-superspec-schema-taskbook.md`
- `docs/rectification/skill-forge-phase-2-superpowers-integration-taskbook.md` -> `docs/99-archive/taskbooks/skill-forge-phase-2-superpowers-integration-taskbook.md`
- `docs/rectification/skill-forge-phase-3-first-real-governed-change-taskbook.md` -> `docs/99-archive/taskbooks/skill-forge-phase-3-first-real-governed-change-taskbook.md`
- `docs/rectification/skill-forge-phase-4-governance-enforcement-hooks-taskbook.md` -> `docs/99-archive/taskbooks/skill-forge-phase-4-governance-enforcement-hooks-taskbook.md`
- `docs/rectification/skill-forge-phase-5-lifecycle-service-adapter-taskbook.md` -> `docs/99-archive/taskbooks/skill-forge-phase-5-lifecycle-service-adapter-taskbook.md`
- `docs/rectification/skill-forge-phase-6-dirty-worktree-triage-taskbook.md` -> `docs/99-archive/taskbooks/skill-forge-phase-6-dirty-worktree-triage-taskbook.md`

The Batch 1 task also creates the four subdirectories under
`docs/99-archive/` (`old-designs/`, `taskbooks/`, `reports/`,
`superseded-roadmaps/`) so the archive layout matches the README.

Batch 1 is the next step. It is docs-only, mechanical, and
permission-safe (no rewrites, no deletes, no content loss).

### Batch 2: summarize then archive

These files contain content that may still be useful as historical
context, but most of it is now redundant with the current authority
docs. Batch 2 is a future task that, for each file, reads the
existing content, extracts anything that is not already covered by
the current authority docs, and folds the extract into a short
summary at the top of the new authority doc (or a one-page summary
in `docs/99-archive/`). The original file is then moved to
`docs/99-archive/old-designs/` (or `superseded-roadmaps/`).

- `docs/skill_forge_design_doc.md` -> summarize into
  `docs/01-architecture/architecture-overview.md` (or a "Historical
  context" section in a new file) and move the original to
  `docs/99-archive/old-designs/skill_forge_design_doc.md`.
- `docs/skill_lifecycle_governance_plan.md` -> confirm the
  lifecycle authority in `docs/06-domain/lifecycle-rules.md` already
  covers its content, and move the original to
  `docs/99-archive/superseded-roadmaps/skill_lifecycle_governance_plan.md`.

Batch 2 requires a separate OpenSpec change because the summarize
step may produce new content in the current-authority docs.

### Batch 3: user-decision items

These files require the user to choose a destination. The
classification above is the recommendation; the user may override
it.

- `docs/skill_forge_next_evolution_plan.md` -> user decision
  between `docs/00-project/` and
  `docs/99-archive/superseded-roadmaps/`.
- `docs/skill_generation_roadmap.md` -> user decision between
  `docs/00-project/` and `docs/99-archive/superseded-roadmaps/`.
- `docs/intelligent-generation-design-v2.md` -> user decision
  between keeping as a deferred roadmap input under
  `docs/00-project/` and moving to `docs/99-archive/`.
- `docs/intelligent-generation-roadmap.md` -> user decision
  between keeping as a deferred roadmap input under
  `docs/00-project/` and moving to
  `docs/99-archive/superseded-roadmaps/`.
- `docs/release-notes.md` -> user decision between
  `docs/00-project/release-notes.md` and
  `docs/99-archive/reports/`.

Batch 3 is a future per-file decision task. It is not a single
move; the user may pick "keep" for some files and "archive" for
others.

## Do Not Move Yet

The following files are flagged "Requires user decision" in the
inventory and must not be moved without explicit confirmation:

- `docs/skill_forge_next_evolution_plan.md`
- `docs/skill_generation_roadmap.md`
- `docs/intelligent-generation-design-v2.md`
- `docs/intelligent-generation-roadmap.md`
- `docs/release-notes.md`

A second category of files is also held back: the current
authority docs in `docs/01-architecture/`, `docs/02-harness/`,
`docs/05-development/`, `docs/06-domain/`, `docs/03-openspec/`,
`docs/04-superpowers/`, and the `docs/00-project/` core (this
plan, the change queue, the disposition matrix, the triage
report, the bulk-import report, the governance reports). These
are current authority and must not be moved.

## Next Step

The next task is **Batch 1 safe moves**. It is a docs-only change
with the following strict-scope allowed-path list:

- `docs/99-archive/old-designs/openspec_change_plan.md` (new path)
- `docs/99-archive/old-designs/intelligent-generation-design.md` (new path)
- `docs/99-archive/taskbooks/skill-forge-phase-*-taskbook.md` (7 new paths)
- `docs/99-archive/old-designs/` (new directory)
- `docs/99-archive/taskbooks/` (new directory)

The move is a `git mv <src> <dst>` for each of the nine files and
the creation of the two new directories. No content rewrite, no
delete, no `git add .`, no `git add -A`. The verification floor is
`python scripts/governance_check.py --quick` plus a final
`git status --short` to confirm the moves landed and no
unintended path was touched. The user explicitly authorizes the
move with "push after every future change" per the standing rule.

Batches 2 and 3 are deferred to follow-up tasks. Batch 2 requires
its own OpenSpec change; Batch 3 requires per-file user decisions
and is not a single task.
