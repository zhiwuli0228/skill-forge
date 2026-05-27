## Why

Skill Forge can update a local research corpus and rank search results, but users cannot easily tell whether an update was partial, which sources were disabled, or why a search result ranked highly. Exposing source-quality status and score breakdowns makes the research layer easier to trust and debug without changing the generation path.

## What Changes

- Improve `skill-forge update` summary output to include updated, skipped, failed, disabled, and partial status.
- Add retry-oriented messages for failed source updates.
- Add a `skill-forge search --explain` option.
- Display deterministic search score components: relevance, authority, completeness, freshness, and platform boost.
- Preserve default search output when `--explain` is not used.
- Do not change `create`, ranking formulas, or the default TF-IDF retrieval path.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `research-corpus-update`: Update reporting distinguishes disabled sources and partial failure states with clearer remediation guidance.
- `search-retrieval`: Search can optionally explain score components for returned results.

## Impact

- Affected CLI:
  - `skill-forge update`
  - `skill-forge search --explain`
- Affected modules:
  - `src/skill_forge/research/updater.py`
  - `src/skill_forge/cli.py`
  - `src/skill_forge/models/search.py`
- Affected tests:
  - `tests/test_research_update.py`
  - `tests/test_search_retrieval.py`
- No new third-party dependencies are expected.
