# Docs Classification Plan

> Status: draft
> Date: 2026-06-06
> Companion to: `docs/README.md` and the directory skeleton under `docs/`
>
> This plan classifies every scattered root-level document under
> `docs/`. It does not move, delete, rewrite, or archive any existing
> document. It is the input to a future Batch 1 safe-move change.

## Purpose

The Skill Forge documentation skeleton is in place under
`docs/01-architecture/`, `docs/02-harness/`, `docs/03-openspec/`,
`docs/04-superpowers/`, `docs/05-development/`, `docs/06-domain/`,
`docs/07-operations/`, and `docs/99-archive/`. The first batch of
current-authority docs has been added. The next task is to clean up
the scattered root-level documents that pre-date the skeleton.

This plan inventories every `docs/*.md` file at the root (except
`docs/README.md`) and classifies each one. For every file it
records:

- The current role.
- The recommended destination (if any).
- The classification.
- The reason for the classification.
- Whether the move is safe to do now.
- Whether a user decision is needed before any move.

The plan groups the files into three migration batches and a
"Do Not Move Yet" list. Batches are intended to be executed as
separate, follow-up tasks with their own OpenSpec changes (or, for
the smallest batch, a single docs-only change) and their own
allowed-path lists.

## Current Docs Root Inventory

The table covers every `docs/*.md` file at the root that is not
`docs/README.md`. `docs/README.md` is the docs navigation file; it
is current authority and stays at the root. The seven
`docs/rectification/*.md` files and the two already-archived root
docs (`docs/openspec_change_plan.md`, `docs/intelligent-generation-design.md`)
are not in this inventory because they were moved by the Batch 1
commit (`31820f3 docs: archive batch 1 scattered docs`) and now
live under `docs/99-archive/old-designs/` and
`docs/99-archive/taskbooks/`.

| File | Current Role | Recommended Destination | Classification | Reason | Move Now? | Requires User Decision? |
|---|---|---|---|---|---|---|
| `docs/skill_forge_design_doc.md` | Original product / architecture design doc (Chinese). It is the upstream design for the system, predating the current architecture. | `docs/99-archive/old-designs/skill_forge_design_doc.md` (after a summarize step) | Architecture source material | The current architecture authority is in `docs/01-architecture/architecture-overview.md`, `module-boundaries.md`, and `data-flow.md`. The design doc predates those and most of its content is now redundant. | no | no (after summarize) |
| `docs/skill_lifecycle_governance_plan.md` | Upstream plan for the lifecycle changes (Chinese). It proposed three progressive OpenSpec changes for lifecycle governance. | `docs/99-archive/superseded-roadmaps/skill_lifecycle_governance_plan.md` (after a summarize step) | Domain source material | The three changes it proposed were adopted. The current lifecycle authority is in `docs/06-domain/lifecycle-rules.md`. | no | no (after summarize) |
| `docs/intelligent-generation-design-v2.md` | V2 design doc for the intelligent generation capability. | `docs/00-project/intelligent-generation-design-v2.md` (as a deferred roadmap input for the future `add-intelligent-generation-fallback` change) or `docs/99-archive/` | Planning / backlog (with archive-candidate option) | The file is a deferred design input. Whether it is kept as a roadmap input or archived depends on the user's intent for the future change. | no | yes |
| `docs/intelligent-generation-roadmap.md` | Roadmap for the intelligent generation capability. | `docs/00-project/intelligent-generation-roadmap.md` (as a deferred roadmap input) or `docs/99-archive/superseded-roadmaps/` | Planning / backlog (with archive-candidate option) | Same as above: it is a deferred roadmap input. | no | yes |
| `docs/skill_forge_next_evolution_plan.md` | Upstream design for the next-stage capabilities (Chinese). | `docs/00-project/skill_forge_next_evolution_plan.md` (as a backlog input) or `docs/99-archive/superseded-roadmaps/` | Planning / backlog (with archive-candidate option) | It is a process tracker for future changes, not current authority. | no | yes |
| `docs/skill_generation_roadmap.md` | Upstream roadmap for fast-generation capabilities (Chinese). | `docs/00-project/skill_generation_roadmap.md` (as a backlog input) or `docs/99-archive/superseded-roadmaps/` | Planning / backlog (with archive-candidate option) | It is a process tracker, not current authority. | no | yes |
| `docs/release-notes.md` | Unreleased release notes draft. | `docs/00-project/release-notes.md` (as the canonical location) or `docs/99-archive/reports/` | Requires user decision | The doc contains unreleased change claims that may or may not be accurate against `main`. The user should confirm the destination and the content. | no | yes |

### Notes on the inventory

- **No file in the current inventory belongs in `docs/01-architecture/`,
  `docs/02-harness/`, `docs/05-development/`, `docs/06-domain/`,
  or `docs/07-operations/`.** The current-authority docs added by
  the previous task are the only entries in those folders. The
  Batch 2 summarize step may produce a short summary that lives in
  the current authority, but the originals move to `docs/99-archive/`.
- **`docs/03-openspec/` and `docs/04-superpowers/` are already
  populated** with current-authority docs and are not in this
  inventory.
- **`docs/00-project/` already contains the recommended-file list
  (status, roadmap, reports, change queue).** The recommended
  destinations for the user-decision entries intentionally point
  back to `docs/00-project/` so the project status remains the
  single source of truth.
- **`docs/99-archive/` already contains `README.md` plus the
  `old-designs/` and `taskbooks/` subdirectories** with the Batch 1
  content. The recommended destinations for the remaining files
  fit the same layout.
- **The empty `docs/rectification/` directory** is left in place. It
  contained the seven taskbooks that were moved in Batch 1. Git
  does not track empty directories, so the directory has no effect
  on the repository. It can be removed in a future cleanup change.

## Recommended Migration Batches

The migration is split into three batches. Each batch is a separate
follow-up task with its own OpenSpec change (or, for the smallest
batch, a single docs-only change) and its own allowed-path list.

### Batch 1: Safe Moves

After the Batch 1 commit (`31820f3`), **there are no remaining safe
moves**. The previous Batch 1 moved every file whose destination
was unambiguous (`docs/openspec_change_plan.md`,
`docs/intelligent-generation-design.md`, and the seven
`docs/rectification/skill-forge-phase-*-taskbook.md` files). The
remaining root-level files each require either a summarize step
(Batch 2) or a user decision (Batch 3).

If a future task finds a new safe move, it should be added here
and executed as a separate docs-only change.

### Batch 2: Summarize Then Archive

These files contain content that may still be useful as historical
context, but most of it is now redundant with the current
authority docs. Batch 2 is a future task that, for each file,
reads the existing content, extracts anything that is not already
covered by the current authority docs, and folds the extract into
a short summary at the top of the new authority doc (or a
one-page summary in `docs/99-archive/`). The original file is
then moved to `docs/99-archive/old-designs/` (or
`superseded-roadmaps/`).

- `docs/skill_forge_design_doc.md` -> summarize into
  `docs/01-architecture/architecture-overview.md` (or a
  "Historical context" section in a new file) and move the
  original to `docs/99-archive/old-designs/skill_forge_design_doc.md`.
- `docs/skill_lifecycle_governance_plan.md` -> confirm the
  lifecycle authority in `docs/06-domain/lifecycle-rules.md`
  already covers its content, and move the original to
  `docs/99-archive/superseded-roadmaps/skill_lifecycle_governance_plan.md`.

Batch 2 requires a separate OpenSpec change because the
summarize step may produce new content in the current-authority
docs.

### Batch 3: User Decision Required

These files require the user to choose a destination. The
classification above is the recommendation; the user may
override it.

- `docs/intelligent-generation-design-v2.md` -> user decision
  between `docs/00-project/intelligent-generation-design-v2.md`
  and `docs/99-archive/`.
- `docs/intelligent-generation-roadmap.md` -> user decision
  between `docs/00-project/intelligent-generation-roadmap.md`
  and `docs/99-archive/superseded-roadmaps/`.
- `docs/skill_forge_next_evolution_plan.md` -> user decision
  between `docs/00-project/skill_forge_next_evolution_plan.md`
  and `docs/99-archive/superseded-roadmaps/`.
- `docs/skill_generation_roadmap.md` -> user decision between
  `docs/00-project/skill_generation_roadmap.md` and
  `docs/99-archive/superseded-roadmaps/`.
- `docs/release-notes.md` -> user decision between
  `docs/00-project/release-notes.md` and
  `docs/99-archive/reports/`.

Batch 3 is a future per-file decision task. It is not a single
move; the user may pick "keep" for some files and "archive" for
others.

## Proposed Destination Map

The map is the single source of truth for the proposed move. The
`Action` column uses four values: `move`, `summarize-then-archive`,
`keep-root-temporarily`, `user-decision`. The `Notes` column
captures the reason and the dependency.

| Source File | Proposed Destination | Action | Notes |
|---|---|---|---|
| `docs/skill_forge_design_doc.md` | `docs/99-archive/old-designs/skill_forge_design_doc.md` | summarize-then-archive | Original architecture design; current authority is in `docs/01-architecture/`. Requires an OpenSpec change to produce the summary. |
| `docs/skill_lifecycle_governance_plan.md` | `docs/99-archive/superseded-roadmaps/skill_lifecycle_governance_plan.md` | summarize-then-archive | Lifecycle plan whose proposed changes were adopted; current authority is in `docs/06-domain/lifecycle-rules.md`. Requires an OpenSpec change to produce the summary. |
| `docs/intelligent-generation-design-v2.md` | `docs/00-project/intelligent-generation-design-v2.md` or `docs/99-archive/` | user-decision | Deferred design input for the future `add-intelligent-generation-fallback` change. |
| `docs/intelligent-generation-roadmap.md` | `docs/00-project/intelligent-generation-roadmap.md` or `docs/99-archive/superseded-roadmaps/` | user-decision | Deferred roadmap input. |
| `docs/skill_forge_next_evolution_plan.md` | `docs/00-project/skill_forge_next_evolution_plan.md` or `docs/99-archive/superseded-roadmaps/` | user-decision | Upstream evolution design; user chooses backlog vs. archive. |
| `docs/skill_generation_roadmap.md` | `docs/00-project/skill_generation_roadmap.md` or `docs/99-archive/superseded-roadmaps/` | user-decision | Upstream generation roadmap; user chooses backlog vs. archive. |
| `docs/release-notes.md` | `docs/00-project/release-notes.md` or `docs/99-archive/reports/` | user-decision | Unreleased release notes; user chooses canonical location vs. archive. |
| `docs/openspec_change_plan.md` (already moved) | `docs/99-archive/old-designs/openspec_change_plan.md` | move (done) | Moved in commit `31820f3`. Listed for traceability only. |
| `docs/intelligent-generation-design.md` (already moved) | `docs/99-archive/old-designs/intelligent-generation-design.md` | move (done) | V1 design; superseded by V2. Moved in commit `31820f3`. |
| `docs/rectification/skill-forge-phase-*-taskbook.md` (7 files, already moved) | `docs/99-archive/taskbooks/skill-forge-phase-*-taskbook.md` | move (done) | Process-only artifacts. Moved in commit `31820f3`. |

No file in the current inventory is classified as
`keep-root-temporarily`. Every remaining file has either a Batch 2
or Batch 3 path.

## Do Not Move Yet

The following files are flagged "Requires User Decision" in the
inventory and must not be moved without explicit confirmation:

- `docs/skill_forge_next_evolution_plan.md`
- `docs/skill_generation_roadmap.md`
- `docs/intelligent-generation-design-v2.md`
- `docs/intelligent-generation-roadmap.md`
- `docs/release-notes.md`

The following files are flagged as Batch 2 and must not be moved
without the summarize step being completed first:

- `docs/skill_forge_design_doc.md`
- `docs/skill_lifecycle_governance_plan.md`

A second category of files is also held back: the current
authority docs in `docs/01-architecture/`, `docs/02-harness/`,
`docs/03-openspec/`, `docs/04-superpowers/`, `docs/05-development/`,
`docs/06-domain/`, `docs/07-operations/`, the `docs/00-project/`
core (the change queue, the disposition matrix, the triage
report, the bulk-import report, the governance reports, this
plan), and `docs/README.md`. These are current authority and must
not be moved.

The empty `docs/rectification/` directory is also held back. It
can be removed in a future cleanup change.

## Next Step

The next task is **Batch 2 summarize then archive** for the two
Batch 2 files. The two Batch 1 candidates from the previous
revision of this plan were already executed in commit `31820f3`,
so the next task is Batch 2. Batch 2 is a non-trivial change
because the summarize step may produce new content in
`docs/01-architecture/architecture-overview.md` and
`docs/06-domain/lifecycle-rules.md`; per `AGENTS.md` Section 6,
the change requires an OpenSpec change folder under
`openspec/changes/<change-id>/` before implementation starts.

If the user prefers, the next task can be a per-file Batch 3 user
decision instead. The user is the right party to choose the
destination for each of the five Batch 3 files. A per-file
decision can be executed as a single docs-only change (with
explicit `git mv` for each file the user approves), or as one
change per file.

In every case, the move is a `git mv <src> <dst>` (or a shell
`mv` plus `git add` for untracked files) and must not rewrite
the content of any file. No `git add .`, no `git add -A`, no
delete, no rewrite. The verification floor is
`python scripts/governance_check.py --quick` plus a final
`git status --short` to confirm the moves landed and no
unintended path was touched. The user explicitly authorizes the
move with the standing "push after every future change" rule.

## Migration Execution Status

| Batch | Description | Status |
|---|---|---|
| Batch 1 | Safe moves (openspec_change_plan, intelligent-generation-design, 7 taskbooks) | Completed (commit `31820f3`) |
| Batch 2 | Summarize-then-archive (skill_forge_design_doc, skill_lifecycle_governance_plan) | Completed |
| Batch 3 | Conservative migration (4 deferred roadmaps, release-notes) | Completed |

**Remaining action:** Keep docs root clean. Future docs must follow `docs/README.md` placement rules.
