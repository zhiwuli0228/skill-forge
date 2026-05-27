## 1. Search Models And Corpus Loading

- [x] 1.1 Add search result and corpus document models with fields for title/name, source, platform, summary, content path, score, and ranking signals.
- [x] 1.2 Add SQLite corpus query helpers that join `skill_examples`, `documents`, and `sources`.
- [x] 1.3 Load normalized file content for each indexed document with graceful handling for missing files.
- [x] 1.4 Add tests for corpus loading from SQLite metadata and normalized files.

## 2. TF-IDF Indexing

- [x] 2.1 Implement an index builder using scikit-learn TF-IDF over normalized text plus metadata fields.
- [x] 2.2 Persist `tfidf.pkl` and index metadata under the Skill Forge index directory.
- [x] 2.3 Compute a corpus signature from document ids, hashes, normalized paths, and update timestamps.
- [x] 2.4 Rebuild the index when no usable index exists or when the corpus signature changes.
- [x] 2.5 Add tests for initial index build, persisted index loading, and stale index rebuild.

## 3. Retrieval And Ranking

- [x] 3.1 Implement query retrieval that returns top-k candidates by TF-IDF relevance.
- [x] 3.2 Add deterministic ranking boosts for authority, content completeness, freshness, and optional platform match.
- [x] 3.3 Ensure final scores are stable and sorted descending.
- [x] 3.4 Add tests for top-k handling, relevance ranking, authority/completeness boosts, and platform match boosts.

## 4. CLI Integration

- [x] 4.1 Add `skill-forge search "<query>"`.
- [x] 4.2 Add `--top-k` option that falls back to configured retrieval default when omitted.
- [x] 4.3 Add optional `--platform` option for platform-aware ranking.
- [x] 4.4 Display results with name/title, source, platform, summary, and score.
- [x] 4.5 Display a clear empty-corpus message that suggests `skill-forge update`.
- [x] 4.6 Add CLI tests for normal results, top-k behavior, platform option, and empty corpus output.

## 5. Verification And Tracking

- [x] 5.1 Run `uv run pytest`.
- [x] 5.2 Run `openspec.cmd validate "add-search-retrieval" --strict`.
- [x] 5.3 Update `docs/openspec_change_plan.md` with proposal progress.
