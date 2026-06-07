# Brainstorm: add-skill-collection-governance

> Status: draft
> Schema: skill-forge-governance
> Author: Codex
> Date: 2026-06-07
>
> Brainstorm is required because this change introduces new capability
> areas, modifies retrieval behavior expectations, and defines a new
> governance layer between discovery and blueprint-driven generation.

## Problem

Skill Forge already has two strong but disconnected assets:

- deterministic and blueprint-backed Skill generation
- local corpus discovery, search, and adoption of community Skills

What it lacks is a governed middle layer that answers:

- which discovered or adopted Skills are worth keeping
- how "excellent" Skills are identified and promoted
- how collected Skills feed back into search, generation, and experience
- whether semantic/vector retrieval should exist as an optional layer
  without replacing the current local deterministic retrieval contract

The user explicitly wants this to be handled as a governance change,
not as an ad hoc feature spike, and not as a plain OpenSpec change.

## Context

- `openspec/specs/skill-blueprints/spec.md` defines deterministic
  blueprint loading and enrichment, but not curation of high-quality
  Skill examples.
- `openspec/specs/search-retrieval/spec.md` defines TF-IDF retrieval,
  deterministic quality signals, and optional local rerank. It
  explicitly preserves offline behavior and avoids mandatory vector
  search.
- `openspec/specs/skill-adoption-workflow/spec.md` defines how cached
  corpus Skills are adopted into the local library, but adoption is a
  trust-preserving import, not a quality endorsement.
- `openspec/specs/skill-library-management/spec.md` lets users list,
  show, and diff generated or adopted Skills, but does not provide a
  collection state such as curated or promoted.
- `openspec/specs/experience-accumulation/spec.md` already establishes
  a local experience layer derived from evidence, which makes it a
  natural downstream consumer of curated high-quality Skill examples.
- `README.md` states that vector database retrieval is not implemented.
- The user wants the change expressed in the project's governed form:
  OpenSpec lifecycle plus SuperSpec-style artifacts plus Superpowers
  execution phases.

## Options

### Option A: Retrieval-first, add vector search before curation

- **Changes**: add semantic retrieval, embedding index, and collection
  search modes first; postpone collection scoring and status modeling.
- **Strength**: fast path to better semantic recall.
- **Weakness**: does not define what a "good" Skill is, so semantic
  retrieval improves similarity before quality governance exists.
- **Risk**: the project gets a more complex search stack without a
  stable promoted reference set.

### Option B: Governance-first, add collection and scoring before semantic retrieval

- **Changes**: define collection states (`candidate`, `curated`,
  `promoted`, `rejected`), add deterministic scoring, integrate those
  states into library/search/generation, and make semantic retrieval a
  later optional phase.
- **Strength**: aligns with the project's local-first and deterministic
  posture; defines excellent Skills before changing retrieval strategy.
- **Weakness**: semantic retrieval benefits arrive later.
- **Risk**: if scoring is too weak, the curated set may be noisy until
  later refinement.

### Option C: Blueprint-first, convert selected adopted Skills directly into blueprints

- **Changes**: skip collection state and instead derive blueprints from
  strong adopted Skills as the primary organization mechanism.
- **Strength**: keeps the surface close to generation.
- **Weakness**: blueprints are templates, not provenance-rich examples;
  this collapses two distinct roles.
- **Risk**: strong examples become prematurely normalized into templates
  and lose evidence context.

## Assumptions

- [verified] Existing corpus, search, adopt, library, lifecycle, and
  experience capabilities are already in place and can be composed.
- [verified] The project still treats vector retrieval as not
  implemented, so introducing it is a new capability rather than a
  documentation sync.
- [verified] The user wants a designed change artifact, not immediate
  implementation.
- [unverified] Implementation should be phased so collection governance
  can land before semantic retrieval.
- [unverified] Collection data can start as local manifest files plus
  small metadata/index additions rather than a large schema rewrite.

## Open Questions

- [non-blocking] Should collection membership be stored only in local
  manifests, or also reflected in SQLite for faster query/filter flows?
- [non-blocking] Should the first semantic mode use a local embedding
  provider only, or define a provider interface from day one?
- [non-blocking] Should promoted Skills be eligible for deterministic
  generation enrichment, or only for LLM-assisted reference lookup in
  the first increment?

## Recommendation

- Recommended: **Option B**.
- Reason: the project already has discovery and generation. The missing
  layer is governance over high-quality Skill assets. Semantic retrieval
  should be added as an optional enhancement after the project can
  explain why a Skill was collected and promoted.
