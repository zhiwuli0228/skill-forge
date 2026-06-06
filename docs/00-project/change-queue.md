# Recommended Change Queue

> Status: draft
> Schema: skill-forge-governance
> Date: 2026-06-06
> Companion to:
> `docs/00-project/wip-disposition-matrix.md` and
> `openspec/changes/triage-dirty-worktree-change-queue/`
>
> This document lists the recommended future OpenSpec
> changes in priority order. Each row records the
> change id, a one-line description, the blocking
> dependency, the expected effort, and the source
> buckets (entries from the WIP disposition matrix)
> that the change will absorb.
>
> Phase 6 does not act on this queue. It only
> records it. The actual change is the work of a
> future phase.

## 1. Queue

| # | Change Id | Description | Depends on | Effort | Source buckets |
|---|-----------|-------------|------------|--------|----------------|
| 1 | `archive-pending-active-changes` | Archive the active `add-skill-lifecycle-recommendation` change (already shipped at 44f60fb and consolidated at 2cb3912) and clean up the duplicate untracked `openspec/specs/skill-lifecycle-recommendation/spec.md`. | none | small | A (#75, #84) |
| 2 | `commit-pre-existing-archive-copies` | Commit the 11 untracked `openspec/changes/archive/2026-05-*/` folders and the tracked `openspec/changes/add-community-skill-discovery/` deletions as a single docs commit. | none | small | A (#3-#9, #68-#78) |
| 3 | `add-local-tool-gitignore-excludes` | Add `.claude/` and `.codex/` to `.gitignore` so the local tool directories are no longer reported as untracked. | none | small | D (#31-#54) |
| 4 | `add-skill-adoption-workflow` | Adopt the untracked `src/skill_forge/adoption/`, `tests/test_skill_adoption.py`, and `openspec/specs/skill-adoption-workflow/spec.md` as a governed change. Re-derive from the archive copy at `openspec/changes/archive/2026-05-31-add-skill-adoption-workflow/`. | none | medium | B (#82, #86, #87, #99) |
| 5 | `add-experience-accumulation` | Adopt the untracked `src/skill_forge/experience/`, `src/skill_forge/models/experience.py`, `tests/test_experience.py`, and `openspec/specs/experience-accumulation/spec.md` as a governed change. Re-derive from the archive copy at `openspec/changes/archive/2026-05-31-add-experience-accumulation/`. Fold the tracked modifications to `src/skill_forge/llm/refiner.py` and `tests/test_llm_refiner.py` (when related to experience). | none | medium | B (#19, #28, #80, #88, #89, #94, #96) |
| 6 | `add-skill-promotion-and-rollback` | Adopt the untracked `src/skill_forge/lifecycle/{__init__,models,promotion,service}.py`, `tests/test_lifecycle.py`, `tests/test_promotion.py`, and `openspec/specs/skill-promotion-and-rollback/spec.md` as a governed change. Re-derive from the archive copy at `openspec/changes/archive/2026-05-31-add-skill-promotion-and-rollback/`. Fold the tracked modifications to `openspec/specs/skill-evaluation/spec.md` and `openspec/specs/skill-validation/spec.md`. | none | medium | B (#14, #16, #85, #90-#93, #97, #98) |
| 7 | `add-skill-lifecycle-index` | Adopt the untracked `openspec/specs/skill-lifecycle-index/spec.md` as a governed change. Re-derive from the archive copy at `openspec/changes/archive/2026-05-31-add-skill-lifecycle-index/`. | none | small | B (#83) |
| 8 | `add-content-quality-rules` | Adopt the untracked `openspec/specs/content-quality-rules/spec.md` as a governed change. Fold the tracked modifications to `src/skill_forge/models/quality.py`, `openspec/specs/generation-quality-report/spec.md`, and `tests/test_generation_quality_report.py`. Re-derive from the archive copy at `openspec/changes/archive/2026-05-31-dd-content-quality-rules/`. | none | medium | B (#10, #21, #27, #79) |
| 9 | `add-intelligent-generation-fallback` | Adopt the untracked `src/skill_forge/retrieval/generation.py` and `openspec/specs/intelligent-generation-fallback/spec.md` as a governed change. Fold the tracked modifications to `src/skill_forge/cli.py` and `tests/test_cli.py`. Re-derive from the archive copy at `openspec/changes/archive/2026-05-28-add-intelligent-fallback/`. Use `docs/intelligent-generation-design-v2.md` and `docs/intelligent-generation-roadmap.md` as design inputs. | none | medium | B (#17, #26, #57, #58, #81, #95) |
| 10 | `add-llm-field-generation` | Adopt the untracked portions of `src/skill_forge/llm/refiner.py` (after `add-experience-accumulation` has extracted its slice) and `openspec/specs/llm-assisted-generation/spec.md` as a governed change. Re-derive from the archive copy at `openspec/changes/archive/2026-05-28-add-llm-field-generation/`. | `add-experience-accumulation` (partial dep) | small | B (#11, #19 [partial], #28 [partial]) |
| 11 | `add-retrieval-augmentation` | Adopt the untracked portions of `src/skill_forge/retrieval/retriever.py` and the tracked modifications to `openspec/specs/local-skill-generation/spec.md`, `openspec/specs/search-retrieval/spec.md`, `src/skill_forge/models/search.py`, and `tests/test_search_retrieval.py` as a governed change. Re-derive from the archive copy at `openspec/changes/archive/2026-05-31-add-retrieval-augmentation/`. | none | medium | B (#12, #13, #22, #23, #29) |
| 12 | `add-community-skill-discovery` | Decide whether to re-derive the archived change as a fresh OpenSpec change, or to keep the work archived and let a smaller change adopt any unadopted pieces. | none | large (deferred) | A (#68, partial), none in B |
| 13 | `add-skill-lifecycle-governance` | Adopt the untracked `docs/skill_lifecycle_governance_plan.md` as the parent governance plan for the lifecycle changes. | `add-skill-promotion-and-rollback` | small | B (#67) |
| 14 | `add-cli-storage-paths-extension` | Adopt the tracked modifications to `src/skill_forge/config.py`, `src/skill_forge/storage/corpus_reader.py`, `src/skill_forge/storage/paths.py`, `src/skill_forge/models/generated.py`, `src/skill_forge/models/search.py`, `openspec/specs/skill-library-management/spec.md`, and `tests/test_skill_library.py` as a small governed change. | none | small | B (#15, #18, #20, #22 [partial], #24, #25, #30) |
| 15 | `discard-superseded-design-doc` | Delete `docs/intelligent-generation-design.md` (superseded by `docs/intelligent-generation-design-v2.md`). | `add-intelligent-generation-fallback` | small | D (#56) |
| 16 | `sync-agents-md-and-agent-md` | Decide whether to commit `AGENT.md`, fold it into `AGENTS.md`, or discard it. | none | small | E (#55) |
| 17 | `commit-rectification-taskbooks` | Decide whether to commit the 7 `docs/rectification/skill-forge-phase-*-taskbook.md` files, fold them into a `docs/rectification/README.md`, or discard them. | none | small | E (#59-#65) |
| 18 | `commit-release-notes` | Decide whether to commit `docs/release-notes.md`, fold it into a `CHANGELOG.md`, or discard it. | none | small | E (#66) |
| 19 | `commit-evolution-plans` | Decide whether to commit the modifications to `docs/skill_forge_next_evolution_plan.md` and `docs/skill_generation_roadmap.md`, fold them into a future `add-next-evolution-plan` change, or discard them. | none | small | E (#1, #2) |
| 20 | `consolidate-skill-lifecycle-recommendation` | Already shipped as Phase 5 (commit 2cb3912). No further action. | done (Phase 5) | done | none |

## 2. Recommended Sequencing

The natural dependency order is:

1. `archive-pending-active-changes` (#1) — clears the
   pre-existing active change folder.
2. `commit-pre-existing-archive-copies` (#2) — commits
   the untracked archive folders.
3. `add-local-tool-gitignore-excludes` (#3) — clears
   the local tool directories.
4. `add-skill-adoption-workflow` (#4) — first
   substantive re-derivation.
5. `add-experience-accumulation` (#5) — second
   substantive re-derivation.
6. `add-skill-promotion-and-rollback` (#6) — third
   substantive re-derivation; depends on
   `add-experience-accumulation` for the shared
   `src/skill_forge/llm/refiner.py` slice.
7. `add-skill-lifecycle-index` (#7) — small follow-up.
8. `add-content-quality-rules` (#8) — independent
   capability.
9. `add-intelligent-generation-fallback` (#9) — the
   `cli.py` modification is large; isolate it.
10. `add-llm-field-generation` (#10) — depends on
    `add-experience-accumulation` for the shared LLM
    refiner slice.
11. `add-retrieval-augmentation` (#11) — independent
    capability.
12. `add-community-skill-discovery` (#12) — large and
    deferred; pick a smaller scope when re-deriving.
13. `add-skill-lifecycle-governance` (#13) — depends
    on `add-skill-promotion-and-rollback` for the
    shared lifecycle vocabulary.
14. `add-cli-storage-paths-extension` (#14) — small
    independent change.
15. `discard-superseded-design-doc` (#15) — depends on
    `add-intelligent-generation-fallback`.
16. `sync-agents-md-and-agent-md` (#16) — user
    decision.
17. `commit-rectification-taskbooks` (#17) — user
    decision.
18. `commit-release-notes` (#18) — user decision.
19. `commit-evolution-plans` (#19) — user decision.
20. `consolidate-skill-lifecycle-recommendation` (#20)
    — done.

The D-class (#15) and E-class (#16-#19) entries are
grouped at the end because they depend on user
decisions. The B-class entries are interleaved with
the small A-class cleanup entries (#1-#3) at the
start because the cleanup makes the working tree
navigable for the substantive re-derivations.

## 3. Notes

- The queue is advisory. The user may reorder or
  drop rows.
- The "Source buckets" column references the entry
  numbers in
  `docs/00-project/wip-disposition-matrix.md`. When
  a future change adopts an entry, the entry's
  status moves from "A (untracked)" or "M" to
  "committed in <change-id>".
- The queue does not specify the OpenSpec artifacts
  for each future change. Each future change must
  create its own eight-artifact folder.
- The queue is a one-time snapshot taken at the
  start of Phase 6. A future phase may extend it.
