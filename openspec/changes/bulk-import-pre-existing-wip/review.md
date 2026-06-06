# Review: bulk-import-pre-existing-wip

> Status: draft
> Schema: skill-forge-governance
> Reviewer: Skill Forge Phase 7 (bulk pre-existing WIP import)
> Date: 2026-06-06
>
> The review is the gate between planning and
> execution. It cross-checks proposal, spec, design,
> plan, and tasks for consistency before
> implementation starts. A change with verdict `block`
> cannot proceed to plan. A change with verdict
> `request-changes` cannot proceed to tasks.

## Change Id

`bulk-import-pre-existing-wip`

## Scope Coverage

| Artifact   | File                                                                              | Verdict | Missing Sections |
|------------|-----------------------------------------------------------------------------------|---------|------------------|
| brainstorm | `brainstorm.md`                                                                   | `ok`    | none             |
| proposal   | `proposal.md`                                                                     | `ok`    | none             |
| spec       | `specs/pre-existing-wip-bulk-import/spec.md`                                      | `ok`    | none             |
| design     | `design.md`                                                                       | `ok`    | none             |

`<verdict>` is one of: `ok`, `minor-issues`, `missing`,
`incorrect`.

## Cross-Artifact Consistency

- Capability name in proposal matches the spec file
  folder: **yes**
  (`pre-existing-wip-bulk-import`).
- Data contracts in design match the affected files
  in plan: **yes** (the only data contracts are the
  three updated Phase 6 docs and the one new
  top-level doc; the plan lists them as the only
  writes outside the OpenSpec change folder).
- Allowed-path list in plan matches the files in
  tasks: **yes** (both list the OpenSpec change
  folder, the one new top-level doc, the three
  updated Phase 6 docs, and the A + B entry paths
  as the only allowed paths).
- Verification commands in tasks match the commands
  in plan: **yes** (both list
  `openspec validate bulk-import-pre-existing-wip --strict`,
  `openspec validate --strict --all`,
  `python scripts/governance_check.py --quick`,
  `python scripts/governance_check.py`,
  `uv run pytest`,
  `uv run skill-forge --help`, and
  `git push origin main`).

## Allowed Path List

### Allowed

The bulk slice has a broader scope than Phase 6. The
allowed paths are:

#### OpenSpec change folder

- `openspec/changes/bulk-import-pre-existing-wip/.openspec.yaml`
- `openspec/changes/bulk-import-pre-existing-wip/brainstorm.md`
- `openspec/changes/bulk-import-pre-existing-wip/proposal.md`
- `openspec/changes/bulk-import-pre-existing-wip/design.md`
- `openspec/changes/bulk-import-pre-existing-wip/review.md`
- `openspec/changes/bulk-import-pre-existing-wip/plan.md`
- `openspec/changes/bulk-import-pre-existing-wip/tasks.md`
- `openspec/changes/bulk-import-pre-existing-wip/verification.md`
- `openspec/changes/bulk-import-pre-existing-wip/specs/pre-existing-wip-bulk-import/spec.md`

#### New top-level doc

- `docs/00-project/bulk-import-verification-report.md`

#### Updated Phase 6 docs

- `docs/00-project/wip-disposition-matrix.md`
- `docs/00-project/change-queue.md`
- `docs/00-project/dirty-worktree-triage-report.md`

#### A-class entries (18 total, including the 7
deletions and 11 archive folders)

- 7 deletions under
  `openspec/changes/add-community-skill-discovery/`:
  - `openspec/changes/add-community-skill-discovery/.openspec.yaml`
  - `openspec/changes/add-community-skill-discovery/design.md`
  - `openspec/changes/add-community-skill-discovery/proposal.md`
  - `openspec/changes/add-community-skill-discovery/specs/community-skill-discovery/spec.md`
  - `openspec/changes/add-community-skill-discovery/specs/research-corpus-update/spec.md`
  - `openspec/changes/add-community-skill-discovery/specs/search-retrieval/spec.md`
  - `openspec/changes/add-community-skill-discovery/tasks.md`
- 11 archive folders under
  `openspec/changes/archive/2026-05-*/`:
  - `openspec/changes/archive/2026-05-28-add-community-skill-discovery/`
  - `openspec/changes/archive/2026-05-28-add-intelligent-fallback/`
  - `openspec/changes/archive/2026-05-28-add-llm-field-generation/`
  - `openspec/changes/archive/2026-05-31-add-experience-accumulation/`
  - `openspec/changes/archive/2026-05-31-add-retrieval-augmentation/`
  - `openspec/changes/archive/2026-05-31-add-skill-adoption-workflow/`
  - `openspec/changes/archive/2026-05-31-add-skill-lifecycle-index/`
  - `openspec/changes/archive/2026-05-31-add-skill-lifecycle-recommendation/`
  - `openspec/changes/archive/2026-05-31-add-skill-promotion-and-rollback/`
  - `openspec/changes/archive/2026-05-31-dd-content-quality-rules/`
  - `openspec/changes/archive/2026-05-31-intelligent-generation/`

#### B-class modified tracked files (21 files)

- `openspec/specs/generation-quality-report/spec.md`
- `openspec/specs/llm-assisted-generation/spec.md`
- `openspec/specs/local-skill-generation/spec.md`
- `openspec/specs/search-retrieval/spec.md`
- `openspec/specs/skill-evaluation/spec.md`
- `openspec/specs/skill-library-management/spec.md`
- `openspec/specs/skill-validation/spec.md`
- `src/skill_forge/cli.py`
- `src/skill_forge/config.py`
- `src/skill_forge/llm/refiner.py`
- `src/skill_forge/models/generated.py`
- `src/skill_forge/models/quality.py`
- `src/skill_forge/models/search.py`
- `src/skill_forge/retrieval/retriever.py`
- `src/skill_forge/storage/corpus_reader.py`
- `src/skill_forge/storage/paths.py`
- `tests/test_cli.py`
- `tests/test_generation_quality_report.py`
- `tests/test_llm_refiner.py`
- `tests/test_search_retrieval.py`
- `tests/test_skill_library.py`

#### B-class untracked files (21 files)

- `docs/skill_lifecycle_governance_plan.md`
- `openspec/specs/content-quality-rules/spec.md`
- `openspec/specs/experience-accumulation/spec.md`
- `openspec/specs/intelligent-generation-fallback/spec.md`
- `openspec/specs/skill-adoption-workflow/spec.md`
- `openspec/specs/skill-lifecycle-index/spec.md`
- `openspec/specs/skill-promotion-and-rollback/spec.md`
- `src/skill_forge/adoption/__init__.py`
- `src/skill_forge/adoption/service.py`
- `src/skill_forge/experience/__init__.py`
- `src/skill_forge/experience/service.py`
- `src/skill_forge/lifecycle/__init__.py`
- `src/skill_forge/lifecycle/models.py`
- `src/skill_forge/lifecycle/promotion.py`
- `src/skill_forge/lifecycle/service.py`
- `src/skill_forge/models/experience.py`
- `src/skill_forge/retrieval/generation.py`
- `tests/test_experience.py`
- `tests/test_lifecycle.py`
- `tests/test_promotion.py`
- `tests/test_skill_adoption.py`

### Forbidden

- Every D-class entry: `.claude/**` and `.codex/**`
  (deferred to a future `.gitignore` change).
- Every E-class entry: `AGENT.md`,
  `docs/intelligent-generation-design.md`,
  `docs/intelligent-generation-design-v2.md`,
  `docs/intelligent-generation-roadmap.md`,
  `docs/rectification/skill-forge-phase-*-taskbook.md`
  (7 files), `docs/release-notes.md`,
  `docs/skill_forge_next_evolution_plan.md`,
  `docs/skill_generation_roadmap.md`.
- The duplicate spec
  `openspec/specs/skill-lifecycle-recommendation/spec.md`
  (matrix entry #84) — skipped per recommendation.
- Every pre-existing Phase 0-6 OpenSpec change
  folder: `openspec/changes/add-skill-lifecycle-recommendation/`,
  `openspec/changes/add-governance-enforcement-hooks/`,
  `openspec/changes/consolidate-lifecycle-recommendation-service/`,
  `openspec/changes/example-governance-stack-walkthrough/`,
  `openspec/changes/triage-dirty-worktree-change-queue/`.
- `pyproject.toml`, `uv.lock`, `templates/**`,
  `configs/**`, `scripts/**`, `README*`, `AGENTS*`/
  `CODEX*`/`CLAUDE*`/`OPENCODE*`/`SUPERPOWERS*`,
  `docs/03-openspec/**`, `docs/04-superpowers/**`,
  `.superpowers/**`, `openspec/config.yaml`,
  `openspec/schemas/**`.
- Every other `docs/00-project/**` file
  (`governance-enforcement-verification-report.md`,
  `first-governed-change-verification-report.md`,
  `lifecycle-service-adapter-verification-report.md`).

### Discrepancies

- None. The allowed list enumerates every A + B
  path explicitly. The forbidden list enumerates
  every D + E path, the duplicate spec, every
  pre-existing Phase 0-6 change, and every runtime
  config / governance doc. No path appears in both
  lists.

## Verification Readiness

| Command                                                                       | Tool / Env       | Status     |
|-------------------------------------------------------------------------------|------------------|------------|
| `openspec validate bulk-import-pre-existing-wip --strict`                     | openspec CLI     | `ok`       |
| `openspec validate --strict --all`                                            | openspec CLI     | `ok`       |
| `python scripts/governance_check.py --quick`                                  | python           | `ok`       |
| `python scripts/governance_check.py`                                          | python           | `ok`       |
| `uv run pytest`                                                               | uv / pytest      | `ok`       |
| `uv run skill-forge --help`                                                   | uv / Typer       | `ok`       |
| `git push origin main`                                                        | git              | `ok`       |

## Required Changes

None. The artifacts are mutually consistent. The
allowed-path list is explicit and matches the
strict-scope list. The verification commands are
runnable in the current environment. The push is
authorized by the user.

## Verdict

`approve`
