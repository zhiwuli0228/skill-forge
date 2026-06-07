# Design: add-skill-collection-governance

> Status: draft
> Schema: skill-forge-governance
> Author: Codex
> Date: 2026-06-07
>
> This design describes a governed collection layer for excellent local
> Skills and a phased path toward optional semantic retrieval.

## Context

Skill Forge currently has two productive but weakly connected flows:

```text
create -> validate -> quality report -> eval -> library -> lifecycle
update -> search -> adopt -> library
```

Blueprints enrich generation, but they are templates rather than a
managed sample corpus. Adoption imports trusted content, but adoption is
not equivalent to endorsement. Search can find good references, but the
system cannot yet persist and organize an intentionally curated set of
excellent Skills. As a result, collection-worthy Skills are visible only
as ordinary library entries, and no capability consistently prefers them
for later reuse.

The user wants this gap treated as governed product work rather than as
an isolated retrieval enhancement.

## Goals / Non-Goals

**Goals:**

- Introduce a governed collection layer for local Skills.
- Make excellent Skill selection deterministic and explainable.
- Expose collection state through library and search surfaces.
- Allow generation and experience accumulation to prefer promoted Skills.
- Keep semantic retrieval optional and local-first.
- Preserve blueprint semantics while allowing future promoted Skills to
  inform blueprint evolution.

**Non-Goals:**

- Do not replace blueprints with collected Skills.
- Do not auto-promote Skills solely because they were adopted.
- Do not require remote inference services.
- Do not mutate third-party Skill content during collection.
- Do not introduce a public sharing marketplace in this change.

## Decisions

### 1. Introduce explicit collection states

Skills in the local library can have an independent collection state:

- `candidate`: imported/generated and eligible for review
- `curated`: accepted into a maintained collection
- `promoted`: high-confidence reference suitable for reuse preference
- `rejected`: explicitly excluded from recommendation or promotion

State is orthogonal to origin. A generated Skill and an adopted Skill
can both become `promoted`; neither gets that state automatically.

### 2. Keep collection governance separate from blueprint identity

Blueprints remain templates and defaults. Collected Skills remain
evidence-bearing examples. The system may later mine blueprint ideas
from promoted Skills, but this change does not collapse those concepts
into one object model.

### 3. Use deterministic collection scoring before manual promotion

The first scoring model should combine existing local signals:

- validation result and structural completeness
- content quality metrics
- eval pass/fail summary
- lifecycle state and recommendation
- provenance quality and origin metadata
- reuse or selection history when available

This yields at least two explainable outputs:

- `collection_score`: should this Skill enter or remain in a curated set
- `promotion_score`: is this Skill a strong preferred reference

Manual overrides are allowed but must be recorded with a reason.

### 4. Store collection metadata in local inspectable manifests

The first implementation should use a local collection store under the
Skill Forge home and optionally a project-scoped override path. A small,
inspectable manifest is preferred over hidden state.

Suggested layout:

```text
~/.skill-forge/collections/
  manifests/
  snapshots/
  indexes/
```

Each record should capture:

- skill identifier
- origin and package path
- collection state
- score summary
- tags
- rationale
- verifier/promoter metadata when known
- last verification timestamp

SQLite mirrors may be added later for performance, but the manifest is
the durable source of truth for this increment.

### 5. Integrate collection state into existing library surfaces

The `list`, `show`, and `diff` flows should surface collection metadata
without changing the underlying package format. `skill-forge.json`
should remain compatible, with collection metadata stored either in the
collection store or as additive provenance fields when a local package
needs self-description.

### 6. Search should prefer collection state without losing TF-IDF defaults

Search remains offline and local by default. Collection integration adds
filtering and ranking options such as:

- filter to `curated` or `promoted`
- boost promoted Skills in otherwise similar results
- expose collection state in search result metadata

Default `skill-forge search "<query>"` behavior remains compatible.

### 7. Generation and experience accumulation should prefer promoted Skills

When local reference lookup is used, promoted Skills should be preferred
over ordinary candidates, provided they still satisfy relevance and
quality gates. This keeps collected excellent Skills from being a dead
end and makes them part of the authoring feedback loop.

This preference should first apply to reference selection paths, not to
direct template mutation.

### 8. Semantic retrieval is a later optional layer

Semantic retrieval is valuable for similarity, clustering, duplicate
detection, and promoted reference discovery. It should be implemented as
an optional retrieval mode, not as a replacement for TF-IDF.

The first semantic design should preserve:

- offline-capable operation
- local index ownership
- explicit mode selection or configuration
- explainable fallback when semantic index/provider is unavailable

## Architecture

```text
community/docs sources
  -> update
  -> local corpus
  -> search
  -> adopt
  -> local library
  -> collection scoring
  -> collection store
       -> curated/promoted filtering in search
       -> preferred references for generation
       -> preferred evidence for experience accumulation
       -> optional semantic similarity and clustering
```

## Data Model

### Collection Record

- `skill_id`
- `package_name`
- `origin_type`
- `origin_reference`
- `collection_state`
- `collection_score`
- `promotion_score`
- `score_version`
- `tags`
- `rationale`
- `manual_override`
- `last_verified_at`

### Score Snapshot

- `skill_id`
- `snapshot_at`
- `structure_score`
- `quality_score`
- `eval_score`
- `lifecycle_score`
- `provenance_score`
- `reuse_score`
- `final_collection_score`
- `final_promotion_score`
- `evidence_refs`

### Semantic Index Metadata

- `index_version`
- `provider`
- `embedding_dim`
- `last_built_at`
- `document_count`
- `fallback_mode`

## Phasing

### Phase 1: Collection Governance

- collection record model and storage
- collection scoring
- collection list/show/update commands
- library/search integration for collection state

### Phase 2: Reuse Integration

- promoted reference preference in generation lookup
- promoted evidence preference in experience derivation
- lifecycle/library visibility improvements

### Phase 3: Optional Semantic Retrieval

- local embedding/index build
- semantic search mode
- similarity/clustering and duplicate detection
- fallback behavior and explain output

## Risks / Trade-offs

- Manifest-only storage may be slower for large collections ->
  acceptable for first increment; add index/cache later if needed.
- Scoring weights may be controversial -> version the scoring model and
  record per-dimension evidence.
- Promoted references may bias generation too strongly -> keep promoted
  preference behind existing relevance/quality gates.
- Semantic mode adds operational complexity -> make it optional and
  preserve TF-IDF fallback.

## Migration Plan

- No migration is required for existing generated/adopted packages in
  the first design slice.
- Existing library entries default to no collection state until scored
  or explicitly classified.
- Search and library features should degrade gracefully when the
  collection store does not yet exist.

## Open Questions

- Should collection state appear in `skill-forge.json`, or only in the
  external collection store for the first version?
- Should project-scoped collections override user-scoped collections, or
  should they merge with explicit precedence?
- Should semantic mode be a dedicated command surface or a flag on the
  existing search command?
