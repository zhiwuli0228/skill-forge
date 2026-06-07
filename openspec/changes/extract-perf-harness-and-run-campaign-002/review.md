# Review — extract-perf-harness-and-run-campaign-002

> Self-review checklist. Each item is an explicit pass/fail
> with a brief evidence line.

## Scope Discipline (AGENTS.md §5, §6)

- [x] **Allowed paths are explicit** (5 paths in `plan.md`).
- [x] **Forbidden paths are explicit** (8 path globs in
  `plan.md`).
- [x] **No modification of `src/skill_forge/**`**. The
  harness is stdlib-only and decoupled, matching 001.
- [x] **No modification of `pyproject.toml` / `uv.lock`**.
  No new dependencies.
- [x] **No modification of governance files** other than
  `docs/00-project/current-state.md` (the one-time
  rotation).
- [x] **No modification of 001's frozen artifacts** under
  `outputs/reports/v0.6.0-remediation/**`. Enforced by
  the harness's 001 freeze contract guardrail.

## OpenSpec Compliance (AGENTS.md §6)

- [x] **8-artifact set produced**: `.openspec.yaml`,
  `brainstorm.md`, `proposal.md`, `design.md`, `review.md`
  (this file), `plan.md`, `tasks.md`, `verification.md`,
  plus two new capability specs under `specs/`.
- [x] **Proposal includes Why / What Changes / Capabilities
  / Impact / Non-Goals / Risks / Rollback** (matching the
  add-skill-collection-governance archived reference).
- [x] **Plan restates allowed/forbidden paths** at the top.
- [x] **Tasks are checkboxes** with observable conditions.
- [x] **Spec deltas use `## ADDED Requirements`** (no
  `MODIFIED` because we add 2 new capabilities and modify
  zero existing capabilities).

## Minimal Diff Discipline (AGENTS.md §10)

- [x] **Harness is 6 modules, not 8** (collapsed `_warmup.py`
  and `_campaign_002.py` after Plan agent critique).
- [x] **No new abstractions for a single occurrence**: each
  module has 2+ functions or 1 dataclass + 1 factory.
- [x] **No "while I'm here" refactors**: harness scope is
  strictly the campaign; no reorganization of existing
  code under `src/` or `tests/`.
- [x] **Pre-existing 34 test files are not modified**.

## Source-of-Truth (AGENTS.md §7)

- [x] **001's `_run_experiments.py` is the behavior
  reference**. The new harness reproduces G1–G6 verbatim
  (same gate IDs, same evaluation logic, same artifact
  schema fields).
- [x] **No claims in this change contradict the README**.
  README does not mention `tests/perf/`; the change does
  not claim any change to the README's feature list (the
  README is updated separately, outside this change's
  scope).

## Verification Discipline (AGENTS.md §8)

- [x] **Pre-implementation evidence collected** (319 tests
  across 28 files, all pass — recorded in `verification.md`).
- [x] **Post-implementation verification commands defined**
  (7 steps in `plan.md`'s "Final Verification Commands"
  section).
- [x] **Each verification step has an expected exit code
  and an expected observation**.

## Stop Conditions (AGENTS.md §9)

- [x] **No forbidden path is required for completion**.
- [x] **No new dependency is required**.
- [x] **The change does not contradict any archived
  OpenSpec decision** (the add-skill-collection-governance
  and add-skill-lifecycle-recommendation archives do not
  constrain harness extraction).

## Anti-Patterns (AGENTS.md §11)

- [x] **No "while I'm here" cleanup**.
- [x] **No "OpenSpec is overkill" shortcut** — this change
  has the full 8-artifact set.
- [x] **No "the user probably meant X"** — proposal
  documents why Campaign-002 is needed and what it
  produces.
- [x] **No "I'll add this for later"** — no speculative
  features; each module exists for a defined consumer
  (Campaign-002 is the first consumer of the harness).
- [x] **No unrequested commits** — the implementer does
  not commit unless explicitly asked.

## Design Quality

- [x] **G9 sign error caught and corrected** in planning
  phase (non-decreasing → non-increasing; see
  `design.md` Gate Logic and `tasks.md` 3.5).
- [x] **Pytest auto-collection isolation verified** with
  a `--collect-only` check in the verification plan.
- [x] **RAMP staircase 8/18/28 is linear (+10/+10)**, not
  the original 8/11/28 (which was +3/+17).
- [x] **Warmup metric reports 3 ratios** (firstToLast,
  firstToMean, firstToMedian) for transparency; only
  firstToMedian drives the G9 verdict.
- [x] **001 freeze contract is a guardrail in code**, not
  just a convention in docs.

## Known Limitations

- Bucket-C `test_sqlite_store` disk I/O may confound
  warmup signal — flagged in `design.md` Confounding
  Factors.
- Absolute warmup ms are not cross-campaign-comparable
  (ratios are) — documented in the warmup-profile schema
  description and in the harness README.
- The 001 design surface (`corePoolSize`, `maximumPoolSize`,
  `queueCapacity` fields) remains placeholder; this change
  does not exercise the v0.6.0 concurrency design. A
  follow-up change is required to validate that surface.

## Sign-off

Ready for `opsx:apply` once the implementer is unblocked
on the authorization rotation (already done in PC1).
