# Tasks: add-skill-collection-governance

> Status: draft
> Schema: skill-forge-governance
> Depends on: design.md, specs/**/spec.md, plan.md

## 1. Collection Model and Storage

- [x] 1.1 Define collection state vocabulary and record schema.
- [x] 1.2 Add a local collection store under the Skill Forge home.
- [x] 1.3 Add score snapshot persistence with evidence references.
- [x] 1.4 Add manifest read/write/list helpers with deterministic
  ordering.
- [x] 1.5 Add tests for empty store, round-trip, and corrupted-record
  handling.

## 2. Collection Scoring

- [x] 2.1 Define deterministic scoring inputs from validation, quality,
  eval, lifecycle, provenance, and reuse signals.
- [x] 2.2 Implement `collection_score` calculation.
- [x] 2.3 Implement `promotion_score` calculation.
- [x] 2.4 Add score-version metadata and explain output.
- [x] 2.5 Add tests for stable scoring, missing-signal handling, and
  deterministic tie behavior.

## 3. Collection CLI and Library Integration

- [x] 3.1 Add collection list/show/update commands or subcommands.
- [x] 3.2 Surface collection state in `skill-forge list`.
- [x] 3.3 Surface collection scores and rationale in
  `skill-forge show <skill-name>`.
- [x] 3.4 Ensure adopted and generated Skills participate consistently.
- [x] 3.5 Add CLI and library tests for collection display and update
  flows.

## 4. Search Integration

- [x] 4.1 Add collection-aware result metadata to retrieval models.
- [x] 4.2 Add search filtering for curated/promoted collections.
- [x] 4.3 Add optional ranking boost for promoted Skills.
- [x] 4.4 Preserve default TF-IDF search behavior when collection
  options are not requested.
- [x] 4.5 Add tests for filtering, boosting, and unchanged default
  behavior.

## 5. Reuse Integration

- [x] 5.1 Add promoted-reference preference in LLM-assisted local
  reference lookup.
- [x] 5.2 Ensure promoted preference still respects relevance and
  quality gates.
- [x] 5.3 Prefer curated/promoted Skills as evidence inputs where
  experience accumulation benefits from stronger examples.
- [x] 5.4 Add provenance or reporting hooks that explain when promoted
  references were used.
- [x] 5.5 Add focused tests for generation and experience integration.

## 6. Optional Semantic Retrieval

- [x] 6.1 Define a local semantic index metadata model.
- [x] 6.2 Add optional semantic embedding/index build support.
- [x] 6.3 Add `search --semantic` or equivalent mode with clear fallback
  semantics.
- [x] 6.4 Add similarity/duplicate-detection helpers for local Skills.
- [x] 6.5 Add tests that prove semantic mode remains optional and local.

## 7. Documentation and Verification

- [x] 7.1 Update `README.md` with collection workflow and optional
  semantic retrieval behavior.
- [x] 7.2 Update `README.zh-CN.md` with the same behavior.
- [x] 7.3 Run focused tests for collection, search, library, generation,
  and semantic retrieval flows.
- [x] 7.4 Run `uv run pytest`.
- [x] 7.5 Run `openspec validate add-skill-collection-governance --strict`.
- [x] 7.6 Run `openspec validate --strict --all`.
- [x] 7.7 Record verification outcomes and blockers in `verification.md`.
