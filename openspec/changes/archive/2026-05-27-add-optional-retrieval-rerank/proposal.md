## Why

Skill Forge search now explains deterministic ranking signals, but users still cannot experiment with a second-stage ranking pass without replacing the default TF-IDF path. An optional local rerank mode lets users improve result ordering while preserving the current fast, offline default.

## What Changes

- Add a pluggable reranker interface for search results.
- Add a built-in offline lexical reranker that does not download models or call the network.
- Add `skill-forge search --rerank` to enable reranking for a single command.
- Add retrieval config fields to control rerank availability and default behavior.
- Mark search output with the retrieval mode used.
- Preserve default TF-IDF search behavior when rerank is not enabled.
- Fall back to TF-IDF ranking when rerank fails, with a clear CLI warning.
- Do not change `create`, install, update, or corpus indexing behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `search-retrieval`: Search supports optional reranking after TF-IDF retrieval while keeping TF-IDF as the default and fallback.
- `cli-foundation`: Default configuration includes retrieval rerank controls.

## Impact

- Affected CLI:
  - `skill-forge search --rerank`
- Affected modules:
  - `src/skill_forge/config.py`
  - `src/skill_forge/retrieval/`
  - `src/skill_forge/cli.py`
  - `src/skill_forge/models/search.py`
- Affected tests:
  - `tests/test_config.py`
  - `tests/test_search_retrieval.py`
- No new third-party dependencies are expected.
