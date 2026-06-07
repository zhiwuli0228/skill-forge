# Verification: add-skill-collection-governance

> Status: draft
> Schema: skill-forge-governance
> Author: Codex
> Date: 2026-06-07
>
> This artifact records verification evidence for the planning/design
> phase and the commands that must be rerun after implementation.

## Planning-Phase Evidence

### Commands Run

1. `openspec list --json`
   - Exit status: 0
   - Purpose: confirm active change structure and governance usage.
2. `openspec new change "add-skill-collection-governance"`
   - Exit status: 0
   - Observation: change directory created, but CLI reported a parse
     error in `openspec/config.yaml` and fell back to `schema: spec-driven`.
3. `openspec status --change "add-skill-collection-governance" --json`
   - Exit status: 0
   - Purpose: inspect the default scaffold produced by the CLI.
4. `git diff --name-only`
   - Exit status: 0
   - Purpose: confirm the changed file set in the working tree.
5. `git status --short`
   - Exit status: 0
   - Purpose: record unrelated dirty-worktree entries separately from the
     new change directory.
6. `openspec validate add-skill-collection-governance --strict`
   - Exit status: 0
   - Purpose: verify the new change artifacts themselves.
7. `openspec validate --strict --all`
   - Exit status: 0
   - Purpose: confirm that the repository-wide OpenSpec validation still
     passes after adding the new change.

### Files Created in Planning Phase

- `openspec/changes/add-skill-collection-governance/.openspec.yaml`
- `openspec/changes/add-skill-collection-governance/brainstorm.md`
- `openspec/changes/add-skill-collection-governance/proposal.md`
- `openspec/changes/add-skill-collection-governance/design.md`
- `openspec/changes/add-skill-collection-governance/review.md`
- `openspec/changes/add-skill-collection-governance/plan.md`
- `openspec/changes/add-skill-collection-governance/tasks.md`
- `openspec/changes/add-skill-collection-governance/specs/skill-collection-management/spec.md`
- `openspec/changes/add-skill-collection-governance/specs/skill-collection-scoring/spec.md`
- `openspec/changes/add-skill-collection-governance/specs/semantic-skill-retrieval/spec.md`
- `openspec/changes/add-skill-collection-governance/specs/search-retrieval/spec.md`
- `openspec/changes/add-skill-collection-governance/specs/skill-library-management/spec.md`
- `openspec/changes/add-skill-collection-governance/specs/experience-accumulation/spec.md`
- `openspec/changes/add-skill-collection-governance/specs/llm-assisted-generation/spec.md`
- `openspec/changes/add-skill-collection-governance/verification.md`

## Known Blockers

### Warning: `openspec new change` reported repository YAML parse noise

- Command:
  `openspec new change "add-skill-collection-governance"`
- Observed problem:
  the CLI reported `Failed to parse openspec/config.yaml:
  YAMLParseError: Implicit keys need to be on a single line`.
- Actual impact:
  the warning affected change scaffolding and the CLI created the change
  under `schema: spec-driven`, but both
  `openspec validate add-skill-collection-governance --strict` and
  `openspec validate --strict --all` later succeeded after the change
  metadata and artifacts were corrected manually.
- Scope note:
  `openspec/config.yaml` is outside this change's allowed write scope, so
  the warning is recorded but not fixed here.

## Post-Implementation Verification To Run

1. `git status --short`
2. `git diff --name-only`
3. `openspec validate add-skill-collection-governance --strict`
4. `openspec validate --strict --all`
5. `uv run pytest`
6. `uv run skill-forge --help`
7. `uv run skill-forge search "skill creator"`

## Post-Implementation Verification Evidence

### Commands Run

1. `git status --short`
   - Exit status: 0
   - Observation: working tree shows modified files and new untracked files for the change.

2. `git diff --name-only`
   - Exit status: 0
   - Changed files:
     - README.md
     - README.zh-CN.md
     - src/skill_forge/cli.py
     - src/skill_forge/config.py (pre-existing dirty, not part of this change)
     - src/skill_forge/library/manager.py
     - src/skill_forge/models/library.py
     - src/skill_forge/models/search.py
     - src/skill_forge/storage/paths.py

3. `openspec validate add-skill-collection-governance --strict`
   - Exit status: 0
   - Output: `Change 'add-skill-collection-governance' is valid`

4. `openspec validate --strict --all`
   - Exit status: 0
   - Output: `Totals: 29 passed, 0 failed (29 items)`

5. `uv run pytest`
   - Exit status: 0
   - Output: `386 passed in 16.70s`
   - Focused test counts:
     - test_collection_store.py: 14 passed
     - test_collection_scoring.py: 18 passed
     - test_collection_cli.py: 14 passed
     - test_collection_search.py: 9 passed
     - test_collection_reuse.py: 10 passed
     - test_semantic_retrieval.py: 11 passed

6. `uv run skill-forge --help`
   - Exit status: 0
   - Output: shows `collection` command in the command list

7. `uv run skill-forge search "skill creator"`
   - Exit status: 0
   - Output: `Local research corpus is empty or has no matches.` (expected in empty test environment)

### New Files Created

- `src/skill_forge/models/collection.py` — Collection state, record, and score snapshot models
- `src/skill_forge/storage/collection_store.py` — Local manifest-based collection store
- `src/skill_forge/lifecycle/scoring.py` — Deterministic collection and promotion scoring
- `src/skill_forge/retrieval/collection_integration.py` — Collection-aware search filtering and boosting
- `src/skill_forge/retrieval/generation_integration.py` — Promoted reference and evidence preference
- `src/skill_forge/retrieval/semantic.py` — Optional semantic retrieval with similarity and duplicate detection
- `tests/test_collection_store.py` — Collection store tests
- `tests/test_collection_scoring.py` — Collection scoring tests
- `tests/test_collection_cli.py` — Collection CLI tests
- `tests/test_collection_search.py` — Collection search integration tests
- `tests/test_collection_reuse.py` — Generation and experience reuse tests
- `tests/test_semantic_retrieval.py` — Semantic retrieval tests

## Exit Criteria

- Collection storage, scoring, search integration, and library
  integration tests pass.
- Optional semantic mode passes focused tests when enabled.
- Default non-semantic search remains functional.
- OpenSpec validation succeeds, or any repo-level validation blocker is
  explicitly resolved in a separate scoped change.
