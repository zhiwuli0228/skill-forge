## Why

Skill Forge can currently cache configured documentation pages, but a GitHub community source is still treated as a single fetched page. Users who want to test or reuse community Skills need Skill Forge to discover individual `SKILL.md` packages inside configured repositories and make them searchable as separate examples.

This change adds repository-scoped community Skill discovery without turning Skill Forge into a general web crawler or marketplace.

## What Changes

- Add GitHub repository discovery for configured community Skill sources.
- Discover candidate `SKILL.md` files from configured path patterns.
- Fetch each discovered Skill file as raw content and normalize/cache it separately.
- Parse `SKILL.md` frontmatter and body to create one `skill_examples` record per discovered Skill.
- Include source URL, repository path, platform metadata, tags, and quality score signals for discovered Skills.
- Make `skill-forge search "code review skill" --platform <platform>` able to return a discovered community Skill result.
- Preserve existing docs-source update behavior and unchanged-content skip behavior.
- Do not add full GitHub search, automatic installation, remote marketplace features, or social ranking.

## Capabilities

### New Capabilities
- `community-skill-discovery`: Discover individual Skill packages from configured GitHub repositories and cache them as searchable local examples.

### Modified Capabilities
- `research-corpus-update`: The update command SHALL process GitHub discovery sources as multiple discovered Skill documents instead of one repository HTML page when discovery metadata is configured.
- `search-retrieval`: Search results SHALL include discovered community Skill examples as first-class corpus results with source, platform, summary, and score metadata.

## Impact

- Affected source config:
  - `configs/sources.yaml`
  - User override `~/.skill-forge/sources.yaml`
- Affected modules:
  - `src/skill_forge/models/source.py`
  - `src/skill_forge/research/fetcher.py`
  - New discovery/extraction module under `src/skill_forge/research/`
  - `src/skill_forge/research/updater.py`
  - `src/skill_forge/storage/corpus_store.py`
  - `src/skill_forge/retrieval/`
- Affected tests:
  - `tests/test_research_update.py`
  - `tests/test_search_retrieval.py`
  - New focused tests for GitHub Skill discovery and extraction
- No database table replacement is expected; existing `documents` and `skill_examples` tables should be reused unless implementation reveals a minimal metadata gap.
