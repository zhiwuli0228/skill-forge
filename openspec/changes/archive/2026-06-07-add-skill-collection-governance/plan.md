# Plan: add-skill-collection-governance

> Status: draft
> Schema: skill-forge-governance
> Depends on: proposal.md, design.md, specs/**/spec.md, review.md
>
> The plan is the executable contract for implementation. It defines
> path scope, sequencing, and verification expectations for the
> implementation agent.

## Change Id

`add-skill-collection-governance`

## Allowed Paths

- `openspec/changes/add-skill-collection-governance/**`
- `src/skill_forge/cli.py`
- `src/skill_forge/retrieval/**`
- `src/skill_forge/storage/**`
- `src/skill_forge/adoption/**`
- `src/skill_forge/generator/**`
- `src/skill_forge/lifecycle/**`
- `src/skill_forge/models/**`
- `src/skill_forge/library/**`
- `tests/**`
- `README.md`
- `README.zh-CN.md`

## Forbidden Paths

- `AGENTS.md`
- `CODEX.md`
- `CLAUDE.md`
- `OPENCODE.md`
- `SUPERPOWERS.md`
- `openspec/config.yaml`
- `openspec/schemas/**`
- `configs/**`
- `templates/**`
- `pyproject.toml`
- `uv.lock`
- Any files outside the Allowed Paths list
- Any new networked dependency, hosted vector service configuration, or
  remote-only embedding runtime requirement

## Pre-Conditions

- [x] Review verdict is `approve`.
- [x] Existing local corpus/search/adopt/library features already exist.
- [x] The implementing agent must not fix unrelated repo-level YAML
  issues unless explicitly asked in a separate scoped change.

## Steps

### Step 1: Add collection data model and storage

- **Files**: storage/model modules under the allowed paths.
- **Action**: define collection records, score snapshots, and local
  collection store layout. Add loading, writing, and listing support.
- **Verification**:
  - `uv run pytest <collection storage tests>`
  - expected: collection records round-trip without network access

### Step 2: Add collection scoring

- **Files**: lifecycle/library/model or scoring modules under allowed
  paths.
- **Action**: compute deterministic `collection_score` and
  `promotion_score` from existing local evidence signals.
- **Verification**:
  - `uv run pytest <collection scoring tests>`
  - expected: same evidence yields the same score outputs

### Step 3: Add collection CLI and library integration

- **Files**: CLI and library modules.
- **Action**: expose list/show/update flows for collection state; show
  collection metadata in existing library views.
- **Verification**:
  - `uv run pytest <library and CLI tests>`
  - expected: collection state appears in output and empty-state behavior
    remains clear

### Step 4: Add search integration

- **Files**: retrieval and CLI modules.
- **Action**: let search filter/boost curated and promoted Skills while
  preserving the default TF-IDF contract.
- **Verification**:
  - `uv run pytest <search retrieval tests>`
  - `uv run skill-forge search "<query>"`
  - expected: default search works unchanged; collection-aware options
    produce filtered or boosted results

### Step 5: Add generation and experience preference hooks

- **Files**: generator, retrieval, lifecycle, and experience-related
  modules under allowed paths.
- **Action**: prefer promoted Skills in local reference-selection paths
  and experience derivation where relevant.
- **Verification**:
  - `uv run pytest <generation and experience tests>`
  - expected: promoted references are preferred only when relevance and
    quality gates still pass

### Step 6: Add optional semantic retrieval

- **Files**: retrieval, storage, model, and CLI modules.
- **Action**: add an optional semantic mode with local index metadata,
  similarity lookup, and graceful fallback to existing retrieval.
- **Verification**:
  - `uv run pytest <semantic retrieval tests>`
  - `uv run skill-forge search "<query>" --semantic`
  - expected: semantic mode works when index exists and falls back
    clearly when unavailable

### Step 7: Documentation and verification

- **Files**: README files and change verification artifact.
- **Action**: document collection workflow, semantic mode semantics, and
  offline constraints; run the final verification suite.
- **Verification**:
  - commands listed below
  - expected: tests pass and documentation matches implemented behavior

## Final Verification

- `git status --short`
- `git diff --name-only`
- `openspec validate add-skill-collection-governance --strict`
- `openspec validate --strict --all`
- `uv run pytest`
- `uv run skill-forge --help`
- `uv run skill-forge search "skill creator"`

## Rollback

1. Remove collection state/score source changes.
2. Remove semantic retrieval additions if already implemented.
3. Revert library/search/generation integration changes in reverse step
   order.
4. Keep the existing TF-IDF, adopt, and blueprint behaviors intact.

## Hand-off Note

- The implementation must preserve the project's local-first posture.
- Semantic retrieval is optional; it cannot become the only working
  search mode.
- Collected Skills are examples with governance metadata, not blueprint
  templates.
