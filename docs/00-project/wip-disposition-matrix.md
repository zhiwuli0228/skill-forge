# WIP Disposition Matrix

> Status: draft
> Schema: skill-forge-governance
> Date: 2026-06-06
> Companion to:
> `docs/00-project/dirty-worktree-triage-report.md`
> and
> `openspec/changes/triage-dirty-worktree-change-queue/`
>
> This matrix classifies every dirty entry in the
> working tree at the start of Phase 6 into one of
> five buckets:
>
> - **A. Absorbed by prior phases** — the entry is
>   already represented in a committed change or in a
>   working-tree archive copy of a committed change.
> - **B. Candidate for future governed change** — the
>   entry is a new source module, new spec, or new
>   test that needs an OpenSpec change to be properly
>   tracked.
> - **C. Existing change needs reshape** — the entry
>   is a tracked modification to a file that belongs
>   to an active change and should be folded into
>   that change.
> - **D. Candidate for discard** — the entry is an
>   obsolete or local-only artifact (e.g. `.claude/`,
>   `.codex/`) that should be ignored rather than
>   tracked.
> - **E. Requires user decision** — the entry is
>   ambiguous; the disposition depends on the user's
>   intent.
>
> Phase 6 does not act on this matrix. It only
> records it. The actual change is the work of a
> future OpenSpec change (see
> `docs/00-project/change-queue.md`).

## 1. Modified Tracked Files (`M`, 30 entries)

| # | Path | Status | Class | Reason | Recommended action |
|---|------|--------|-------|--------|--------------------|
| 1 | `docs/skill_forge_next_evolution_plan.md` | M (+10) | E | WIP doc edit; the user has not yet declared the new evolution plan content ready. | Keep on disk; ask the user whether to commit, fold into a future docs change, or discard. |
| 2 | `docs/skill_generation_roadmap.md` | M (+1) | E | Single-line WIP doc edit. | Keep on disk; ask the user. |
| 3 | `openspec/changes/add-community-skill-discovery/.openspec.yaml` | D | A | The active change folder was archived; the working-tree deletion is the result of the archive operation that was not yet committed. | Commit the deletion in a follow-up docs commit. The archived copy is at `openspec/changes/archive/2026-05-28-add-community-skill-discovery/`. |
| 4 | `openspec/changes/add-community-skill-discovery/design.md` | D | A | Same as #3. | Same as #3. |
| 5 | `openspec/changes/add-community-skill-discovery/proposal.md` | D | A | Same as #3. | Same as #3. |
| 6 | `openspec/changes/add-community-skill-discovery/specs/community-skill-discovery/spec.md` | D | A | Same as #3. | Same as #3. |
| 7 | `openspec/changes/add-community-skill-discovery/specs/research-corpus-update/spec.md` | D | A | Same as #3. | Same as #3. |
| 8 | `openspec/changes/add-community-skill-discovery/specs/search-retrieval/spec.md` | D | A | Same as #3. | Same as #3. |
| 9 | `openspec/changes/add-community-skill-discovery/tasks.md` | D | A | Same as #3. | Same as #3. |
| 10 | `openspec/specs/generation-quality-report/spec.md` | M (+61) | B | New content for the generation quality report capability; needs a future governed change. | Fold into the future `add-content-quality-rules` change. |
| 11 | `openspec/specs/llm-assisted-generation/spec.md` | M (+126) | B | New requirements for the LLM-assisted generation capability. | Fold into the future `add-llm-field-generation` change. |
| 12 | `openspec/specs/local-skill-generation/spec.md` | M (+77) | B | New requirements for the local skill generation capability. | Fold into the future `add-retrieval-augmentation` change. |
| 13 | `openspec/specs/search-retrieval/spec.md` | M (+47) | B | New requirements for the search retrieval capability. | Fold into the future `add-retrieval-augmentation` change. |
| 14 | `openspec/specs/skill-evaluation/spec.md` | M (+16) | B | New requirements for the skill evaluation capability. | Fold into the future `add-skill-promotion-and-rollback` change. |
| 15 | `openspec/specs/skill-library-management/spec.md` | M (+38) | B | New requirements for the skill library management capability. | Fold into the future `add-cli-storage-paths-extension` change. |
| 16 | `openspec/specs/skill-validation/spec.md` | M (+30) | B | New requirements for the skill validation capability. | Fold into the future `add-skill-promotion-and-rollback` change. |
| 17 | `src/skill_forge/cli.py` | M (+662) | B | Large CLI surface addition for the new commands. | Fold into the future `add-intelligent-generation-fallback` change (and the related archive re-derivations). |
| 18 | `src/skill_forge/config.py` | M (+4) | B | Small config additions. | Fold into the future `add-cli-storage-paths-extension` change. |
| 19 | `src/skill_forge/llm/refiner.py` | M (+243) | B | LLM refiner expansion. | Fold into the future `add-llm-field-generation` and `add-experience-accumulation` changes. |
| 20 | `src/skill_forge/models/generated.py` | M (+22) | B | New model fields. | Fold into the future `add-cli-storage-paths-extension` change. |
| 21 | `src/skill_forge/models/quality.py` | M (+221) | B | New quality model. | Fold into the future `add-content-quality-rules` change. |
| 22 | `src/skill_forge/models/search.py` | M (+8) | B | New search model fields. | Fold into the future `add-retrieval-augmentation` change. |
| 23 | `src/skill_forge/retrieval/retriever.py` | M (+5) | B | Small retriever change. | Fold into the future `add-retrieval-augmentation` change. |
| 24 | `src/skill_forge/storage/corpus_reader.py` | M (+12) | B | Storage reader change. | Fold into the future `add-cli-storage-paths-extension` change. |
| 25 | `src/skill_forge/storage/paths.py` | M (+10) | B | Storage path change. | Fold into the future `add-cli-storage-paths-extension` change. |
| 26 | `tests/test_cli.py` | M (+316) | B | New CLI tests. | Fold into the future `add-intelligent-generation-fallback` change. |
| 27 | `tests/test_generation_quality_report.py` | M (+114) | B | New generation quality report tests. | Fold into the future `add-content-quality-rules` change. |
| 28 | `tests/test_llm_refiner.py` | M (+161) | B | New LLM refiner tests. | Fold into the future `add-llm-field-generation` and `add-experience-accumulation` changes. |
| 29 | `tests/test_search_retrieval.py` | M (+129) | B | New search retrieval tests. | Fold into the future `add-retrieval-augmentation` change. |
| 30 | `tests/test_skill_library.py` | M (+30) | B | New skill library tests. | Fold into the future `add-cli-storage-paths-extension` change. |

## 2. Untracked Local Tool Directories (D-class, 24 entries)

| # | Path | Status | Class | Reason | Recommended action |
|---|------|--------|-------|--------|--------------------|
| 31 | `.claude/commands/opsx/apply.md` | A (untracked) | D | Local Claude Code slash-command file; generated by the user's local dev environment. | Add to `.gitignore` via the future `add-local-tool-gitignore-excludes` change. |
| 32 | `.claude/commands/opsx/archive.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 33 | `.claude/commands/opsx/bulk-archive.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 34 | `.claude/commands/opsx/continue.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 35 | `.claude/commands/opsx/explore.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 36 | `.claude/commands/opsx/ff.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 37 | `.claude/commands/opsx/new.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 38 | `.claude/commands/opsx/onboard.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 39 | `.claude/commands/opsx/propose.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 40 | `.claude/commands/opsx/sync.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 41 | `.claude/commands/opsx/verify.md` | A (untracked) | D | Same as #31. | Same as #31. |
| 42 | `.claude/settings.local.json` | A (untracked) | D | Local Claude Code settings file; user-specific permissions. | Same as #31. |
| 43 | `.claude/skills/openspec-apply-change/SKILL.md` | A (untracked) | D | Local Claude Code skill file. | Same as #31. |
| 44 | `.claude/skills/openspec-archive-change/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 45 | `.claude/skills/openspec-bulk-archive-change/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 46 | `.claude/skills/openspec-continue-change/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 47 | `.claude/skills/openspec-explore/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 48 | `.claude/skills/openspec-ff-change/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 49 | `.claude/skills/openspec-new-change/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 50 | `.claude/skills/openspec-onboard/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 51 | `.claude/skills/openspec-propose/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 52 | `.claude/skills/openspec-sync-specs/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 53 | `.claude/skills/openspec-verify-change/SKILL.md` | A (untracked) | D | Same as #43. | Same as #31. |
| 54 | `.codex/skills/openspec-*/SKILL.md` (11 files) | A (untracked) | D | Local Codex skill files; mirror of the `.claude/skills/` set. | Same as #31. |

## 3. Untracked Top-Level Doc Files (E-class, 12 entries)

| # | Path | Status | Class | Reason | Recommended action |
|---|------|--------|-------|--------|--------------------|
| 55 | `AGENT.md` | A (untracked) | E | A new top-level agent-readme file; the user has not declared whether to commit, fold into `AGENTS.md`, or discard. | Ask the user; recommend folding into a future `sync-agents-md-and-agent-md` docs change. |
| 56 | `docs/intelligent-generation-design.md` | A (untracked) | E | Early-version design doc for the intelligent generation capability. | Superseded by `docs/intelligent-generation-design-v2.md`; recommend discard. |
| 57 | `docs/intelligent-generation-design-v2.md` | A (untracked) | E | Later-version design doc; the user has not declared it ready. | Ask the user; recommend folding into a future `add-intelligent-generation-fallback` change as a design input. |
| 58 | `docs/intelligent-generation-roadmap.md` | A (untracked) | E | Roadmap doc for the intelligent generation capability. | Ask the user; recommend folding into a future `add-intelligent-generation-fallback` change as a roadmap input. |
| 59 | `docs/rectification/skill-forge-phase-0-governance-entry-taskbook.md` | A (untracked) | E | Phase 0 taskbook; the user has not declared it ready. | Keep on disk; ask the user; recommend committing alongside the other `docs/rectification/` files in a future docs change. |
| 60 | `docs/rectification/skill-forge-phase-1-openspec-superspec-schema-taskbook.md` | A (untracked) | E | Phase 1 taskbook. | Same as #59. |
| 61 | `docs/rectification/skill-forge-phase-2-superpowers-integration-taskbook.md` | A (untracked) | E | Phase 2 taskbook. | Same as #59. |
| 62 | `docs/rectification/skill-forge-phase-3-first-real-governed-change-taskbook.md` | A (untracked) | E | Phase 3 taskbook. | Same as #59. |
| 63 | `docs/rectification/skill-forge-phase-4-governance-enforcement-hooks-taskbook.md` | A (untracked) | E | Phase 4 taskbook. | Same as #59. |
| 64 | `docs/rectification/skill-forge-phase-5-lifecycle-service-adapter-taskbook.md` | A (untracked) | E | Phase 5 taskbook. | Same as #59. |
| 65 | `docs/rectification/skill-forge-phase-6-dirty-worktree-triage-taskbook.md` | A (untracked) | E | Phase 6 taskbook (this phase). | Same as #59. |
| 66 | `docs/release-notes.md` | A (untracked) | E | Release notes draft; the user has not declared it ready. | Ask the user; recommend committing alongside a tagged release. |
| 67 | `docs/skill_lifecycle_governance_plan.md` | A (untracked) | B | Parent governance plan for the lifecycle changes; the user has not declared it ready. | Fold into a future `add-skill-lifecycle-governance` change. |

## 4. Untracked Archived Change Folders (A-class, 11 entries)

| # | Path | Status | Class | Reason | Recommended action |
|---|------|--------|-------|--------|--------------------|
| 68 | `openspec/changes/archive/2026-05-28-add-community-skill-discovery/` (7 files) | A (untracked) | A | Archived copy of the `add-community-skill-discovery` change. The active folder was deleted in the working tree (entries #3-#9). | Keep on disk; commit the untracked archive copy and the tracked deletions in a follow-up docs commit. |
| 69 | `openspec/changes/archive/2026-05-28-add-intelligent-fallback/` (5 files) | A (untracked) | A | Archived copy of the `add-intelligent-fallback` change. | Keep on disk; commit the untracked archive copy. |
| 70 | `openspec/changes/archive/2026-05-28-add-llm-field-generation/` (5 files) | A (untracked) | A | Archived copy of the `add-llm-field-generation` change. | Keep on disk; commit the untracked archive copy. |
| 71 | `openspec/changes/archive/2026-05-31-add-experience-accumulation/` (7 files) | A (untracked) | A | Archived copy of the `add-experience-accumulation` change. | Keep on disk; commit the untracked archive copy. |
| 72 | `openspec/changes/archive/2026-05-31-add-retrieval-augmentation/` (6 files) | A (untracked) | A | Archived copy of the `add-retrieval-augmentation` change. | Keep on disk; commit the untracked archive copy. |
| 73 | `openspec/changes/archive/2026-05-31-add-skill-adoption-workflow/` (6 files) | A (untracked) | A | Archived copy of the `add-skill-adoption-workflow` change. | Keep on disk; commit the untracked archive copy. |
| 74 | `openspec/changes/archive/2026-05-31-add-skill-lifecycle-index/` (4 files) | A (untracked) | A | Archived copy of the `add-skill-lifecycle-index` change. | Keep on disk; commit the untracked archive copy. |
| 75 | `openspec/changes/archive/2026-05-31-add-skill-lifecycle-recommendation/` (4 files) | A (untracked) | A | Archived copy of the `add-skill-lifecycle-recommendation` change. The change is the same as the active `add-skill-lifecycle-recommendation` (Phase 3) and the Phase 5 `consolidate-lifecycle-recommendation-service`. | Keep on disk; commit the untracked archive copy. |
| 76 | `openspec/changes/archive/2026-05-31-add-skill-promotion-and-rollback/` (4 files) | A (untracked) | A | Archived copy of the `add-skill-promotion-and-rollback` change. | Keep on disk; commit the untracked archive copy. |
| 77 | `openspec/changes/archive/2026-05-31-dd-content-quality-rules/` (5 files) | A (untracked) | A | Archived copy of the `add-content-quality-rules` change. | Keep on disk; commit the untracked archive copy. |
| 78 | `openspec/changes/archive/2026-05-31-intelligent-generation/` (1 file: `.openspec.yaml`) | A (untracked) | A | Degenerate archive copy with only the header; the body files were never archived. | Keep on disk; commit the untracked archive copy. A follow-up decision is whether to remove this degenerate copy or flesh it out. |

## 5. Untracked Specs (B-class, 7 entries)

| # | Path | Status | Class | Reason | Recommended action |
|---|------|--------|-------|--------|--------------------|
| 79 | `openspec/specs/content-quality-rules/spec.md` | A (untracked) | B | New spec for the content quality rules capability. | Fold into the future `add-content-quality-rules` change. |
| 80 | `openspec/specs/experience-accumulation/spec.md` | A (untracked) | B | New spec for the experience accumulation capability. | Fold into the future `add-experience-accumulation` change. |
| 81 | `openspec/specs/intelligent-generation-fallback/spec.md` | A (untracked) | B | New spec for the intelligent generation fallback capability. | Fold into the future `add-intelligent-generation-fallback` change. |
| 82 | `openspec/specs/skill-adoption-workflow/spec.md` | A (untracked) | B | New spec for the skill adoption workflow capability. | Fold into the future `add-skill-adoption-workflow` change. |
| 83 | `openspec/specs/skill-lifecycle-index/spec.md` | A (untracked) | B | New spec for the skill lifecycle index capability. | Fold into the future `add-skill-lifecycle-index` change. |
| 84 | `openspec/specs/skill-lifecycle-recommendation/spec.md` | A (untracked) | A | Duplicate of the spec already shipped in Phase 3 (44f60fb); the user has a stray untracked copy on disk. | Discard the untracked copy. |
| 85 | `openspec/specs/skill-promotion-and-rollback/spec.md` | A (untracked) | B | New spec for the skill promotion and rollback capability. | Fold into the future `add-skill-promotion-and-rollback` change. |

## 6. Untracked Source Modules (B-class, 10 entries)

| # | Path | Status | Class | Reason | Recommended action |
|---|------|--------|-------|--------|--------------------|
| 86 | `src/skill_forge/adoption/__init__.py` | A (untracked) | B | New module init. | Fold into the future `add-skill-adoption-workflow` change. |
| 87 | `src/skill_forge/adoption/service.py` | A (untracked) | B | New service module. | Same as #86. |
| 88 | `src/skill_forge/experience/__init__.py` | A (untracked) | B | New module init. | Fold into the future `add-experience-accumulation` change. |
| 89 | `src/skill_forge/experience/service.py` | A (untracked) | B | New service module. | Same as #88. |
| 90 | `src/skill_forge/lifecycle/__init__.py` | A (untracked) | B | New module init; the lifecycle module is the parent of the Phase 3/5 changes. | Fold into the future `add-skill-promotion-and-rollback` change. |
| 91 | `src/skill_forge/lifecycle/models.py` | A (untracked) | B | New lifecycle models. | Same as #90. |
| 92 | `src/skill_forge/lifecycle/promotion.py` | A (untracked) | B | New lifecycle promotion module. | Same as #90. |
| 93 | `src/skill_forge/lifecycle/service.py` | A (untracked) | B | New lifecycle service. | Same as #90. |
| 94 | `src/skill_forge/models/experience.py` | A (untracked) | B | New experience model. | Fold into the future `add-experience-accumulation` change. |
| 95 | `src/skill_forge/retrieval/generation.py` | A (untracked) | B | New retrieval generation module. | Fold into the future `add-intelligent-generation-fallback` change. |

## 7. Untracked Tests (B-class, 4 entries)

| # | Path | Status | Class | Reason | Recommended action |
|---|------|--------|-------|--------|--------------------|
| 96 | `tests/test_experience.py` | A (untracked) | B | New test for the experience service. | Fold into the future `add-experience-accumulation` change. |
| 97 | `tests/test_lifecycle.py` | A (untracked) | B | New test for the lifecycle service. | Fold into the future `add-skill-promotion-and-rollback` change. |
| 98 | `tests/test_promotion.py` | A (untracked) | B | New test for the lifecycle promotion module. | Same as #97. |
| 99 | `tests/test_skill_adoption.py` | A (untracked) | B | New test for the skill adoption service. | Fold into the future `add-skill-adoption-workflow` change. |

## 8. Class Counts

| Class | Count | Description |
|-------|-------|-------------|
| A | 18 | Absorbed by prior phases (entries #3-#9, #68-#78, #84). |
| B | 56 | Candidate for future governed change (entries #10-#30, #67, #79-#83, #85-#99). |
| C | 0 | Existing change needs reshape. |
| D | 24 | Candidate for discard via a follow-up `.gitignore` change (entries #31-#54). |
| E | 14 | Requires user decision (entries #1-#2, #55-#66). |
| **Total** | **112** | All dirty entries from `git status --short`. |

## 9. Notes

- The matrix is a one-time snapshot taken at the
  start of Phase 6. The dirty worktree evolves; a
  future phase may extend the matrix.
- The "Recommended action" column is advisory; the
  user may override it.
- The matrix is the per-entry view; the recommended
  sequencing of future changes is in
  `docs/00-project/change-queue.md`.

## 10. Phase 7 Bulk Slice Disposition

On 2026-06-06 the A + B entries from the §1-§7
matrix were absorbed in a single OpenSpec change
(`bulk-import-pre-existing-wip`). The D + E
entries were deferred. The duplicate spec
(`openspec/specs/skill-lifecycle-recommendation/spec.md`,
entry #84) was skipped per the recommendation in
§5.

### 10.1 Absorbed entries (60 total: 18 A + 42 B)

| Range | Class | Status | Where absorbed |
|-------|-------|--------|----------------|
| #3-#9 (7 deletions) | A | absorbed | bulk-import-pre-existing-wip |
| #68-#78 (11 archive folders) | A | absorbed | bulk-import-pre-existing-wip |
| #10-#30 (21 modified tracked) | B | absorbed | bulk-import-pre-existing-wip |
| #67 (1 untracked doc) | B | absorbed | bulk-import-pre-existing-wip |
| #79-#83, #85 (6 untracked specs) | B | absorbed | bulk-import-pre-existing-wip |
| #86-#95 (10 untracked source modules) | B | absorbed | bulk-import-pre-existing-wip |
| #96-#99 (4 untracked tests) | B | absorbed | bulk-import-pre-existing-wip |

### 10.2 Deferred entries (38 total: 24 D + 14 E)

| Range | Class | Status | Where deferred |
|-------|-------|--------|----------------|
| #31-#54 (24 local tool files) | D | deferred | future `add-local-tool-gitignore-excludes` change |
| #1-#2 (2 modified WIP docs) | E | deferred | user per-file decision |
| #55-#66 (12 untracked WIP docs / design / roadmap / taskbooks) | E | deferred | user per-file decision |

### 10.3 Skipped entries (1 total)

| # | Class | Status | Why |
|---|-------|--------|-----|
| #84 | A | skipped | Duplicate of the spec shipped in Phase 3 (44f60fb). The user should `rm openspec/specs/skill-lifecycle-recommendation/spec.md` to discard the untracked copy. |

### 10.4 Count correction

The §8 class counts say "A=18, B=56" but the
per-entry table in §1-§7 sums to A=18 (entries
#3-#9, #68-#78, #84) and B=42 (entries #10-#30,
#67, #79-#83, #85-#99; the 21 modified tracked +
1 doc + 6 specs + 10 source + 4 tests = 42). The
§8 "B=56" is a typo. The corrected total is
**112 = 18 A + 42 B + 0 C + 24 D + 14 E + 1 dup
skip**, or equivalently **60 absorbed + 38
deferred + 1 skipped = 99** (the
already-tracked pre-existing entries are not
counted in the matrix because they are not dirty).
