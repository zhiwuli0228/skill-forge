# Proposal: add-skill-collection-governance

> Status: draft
> Schema: skill-forge-governance
> Author: Codex
> Date: 2026-06-07
>
> This proposal introduces a governed Skill collection layer that sits
> between discovery/adoption and generation/reuse. It is intended as a
> supplement to existing blueprint, corpus, and lifecycle capabilities,
> not as a new standalone product.

## Why

Skill Forge can already:

- generate Skills with deterministic and blueprint-backed flows
- discover community Skills into the local corpus
- search local corpus entries
- adopt trusted cached Skills into the local library
- evaluate generated packages and derive lifecycle/experience signals

Those capabilities are adjacent but not yet organized around a durable
asset strategy. The project has no first-class answer to:

- which Skills count as excellent references
- how discovered/adopted/generated Skills are promoted into a curated set
- how curation feeds search, generation, and experience accumulation
- where optional semantic retrieval fits without replacing the local
  deterministic TF-IDF default

The result is that blueprint evolution and retrieval augmentation are
underpowered by the lack of a curated high-quality Skill set. This
change puts that work on the roadmap as a governed capability.

## What Changes

- Add a new Skill collection capability that classifies local library
  Skills into governed states such as `candidate`, `curated`,
  `promoted`, and `rejected`.
- Add deterministic collection scoring derived from existing local
  signals: validation, quality report, eval results, lifecycle facts,
  provenance, and reuse history.
- Integrate collection state into local library inspection and search so
  users can filter or prioritize curated/promoted Skills.
- Define how generation and experience accumulation consume promoted
  Skills as preferred local references.
- Add an optional semantic retrieval capability as a later phase,
  explicitly preserving TF-IDF as the default behavior.
- Provide a full eight-artifact governed change under the
  `skill-forge-governance` schema.

## Capabilities

### New Capabilities

- `skill-collection-management`: manage governed collection states for
  local Skills.
- `skill-collection-scoring`: deterministically score Skills for
  curation and promotion decisions.
- `semantic-skill-retrieval`: optional semantic retrieval and similarity
  analysis over local Skills.

### Modified Capabilities

- `search-retrieval`: search can filter or prioritize curated/promoted
  collections and later offer an optional semantic mode.
- `skill-library-management`: library views expose collection state,
  collection score summaries, and promotion metadata.
- `experience-accumulation`: experience derivation can prefer
  curated/promoted Skills as higher-quality evidence.
- `llm-assisted-generation`: reference lookup can prefer promoted Skills
  when local high-quality references exist.

### Removed Capabilities

- None.

## Impact

- Affected specs:
  - new: `skill-collection-management`
  - new: `skill-collection-scoring`
  - new: `semantic-skill-retrieval`
  - modified: `search-retrieval`
  - modified: `skill-library-management`
  - modified: `experience-accumulation`
  - modified: `llm-assisted-generation`
- Expected implementation surfaces:
  - `src/skill_forge/cli.py`
  - `src/skill_forge/retrieval/**`
  - `src/skill_forge/storage/**`
  - `src/skill_forge/adoption/**`
  - `src/skill_forge/library/**` or equivalent package management code
  - `src/skill_forge/lifecycle/**`
  - `src/skill_forge/generator/**`
- Expected tests:
  - collection scoring tests
  - collection manifest/storage tests
  - search and library integration tests
  - generation reference selection tests
  - semantic retrieval tests with offline fixtures

## Non-Goals

- Building a public marketplace.
- Adding social ranking based on stars, forks, downloads, or likes.
- Replacing TF-IDF search as the default retrieval mode.
- Automatically rewriting adopted third-party `SKILL.md` content.
- Automatically converting curated Skills into blueprints.
- Requiring cloud-hosted embedding or vector database services.

## Risks

- [Collection state becomes subjective and inconsistent] ->
  Mitigation: require deterministic scoring inputs and explicit manual
  override reasons.
- [Semantic retrieval expands scope too early] -> Mitigation: phase the
  work so collection governance lands before semantic mode.
- [Collection metadata introduces hidden state] -> Mitigation: use local,
  inspectable manifests and surface state in library/show commands.
- [Generation overfits promoted references] -> Mitigation: treat
  promoted Skills as references, not source text to copy; keep existing
  validation and quality gates.
- [Implementation touches too many surfaces at once] -> Mitigation:
  sequence tasks by phases and verify each phase independently.

## Rollback

1. Remove collection state/score commands and storage additions.
2. Remove collection-related search and library display changes.
3. Disable promoted-reference selection for generation.
4. Remove optional semantic retrieval mode and index artifacts if added.
5. Leave existing corpus, adoption, library, and TF-IDF behavior intact.

## Consistency With Brainstorm

- Brainstorm file: `brainstorm.md`
- Recommended option: governance-first collection design before semantic
  retrieval.
- Deviations and reasons: none. This proposal follows the brainstorm
  recommendation exactly.
