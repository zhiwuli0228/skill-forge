## Why

Skill Forge can now refresh and cache a local research corpus, but users cannot query that corpus directly. This change adds local search so users can inspect relevant Skill references before generation and so later generation flows can reuse a tested retrieval layer.

## What Changes

- Add `skill-forge search "<query>"` for searching the local research corpus.
- Support `--top-k` to control the maximum number of returned results.
- Build a TF-IDF index from locally cached normalized corpus content and SQLite metadata.
- Store the search index under the Skill Forge index directory.
- Automatically rebuild the index when no usable index exists or when corpus metadata has changed.
- Return ranked results containing name/title, source, platform, summary, and score.
- Apply simple ranking boosts for source authority, content completeness, freshness, and optional platform match.
- Show a clear empty-state message when no corpus documents are available.
- Add focused tests for indexing, ranking, empty corpus behavior, top-k handling, and CLI output.

## Capabilities

### New Capabilities

- `search-retrieval`: Covers local TF-IDF indexing, corpus search, result ranking, top-k behavior, empty-state handling, and CLI presentation for local research references.

### Modified Capabilities

- None.

## Impact

- Affected command surface: adds `skill-forge search`.
- Affected source areas: new retrieval/indexing/ranking components, search result models, SQLite corpus queries, index file persistence, and CLI wiring.
- Affected local filesystem: reads normalized corpus files and SQLite metadata, writes `~/.skill-forge/index/tfidf.pkl` and index metadata under `~/.skill-forge/index/`.
- Affected dependencies: uses existing `scikit-learn` for TF-IDF and existing SQLite/corpus data created by `skill-forge update`.
- Out of scope: vector search, LLM reranking, automatic network refresh, modifying `create` to use retrieval results, and advanced pattern extraction.
