## Context

Skill Forge now has a manual research update pipeline that stores source metadata in SQLite and writes raw/normalized corpus files. The next step is to make that local corpus usable through a search command. This change should introduce a retrieval layer that can later be reused by generation, while keeping the current scope limited to user-visible search.

The existing project already includes `scikit-learn`, SQLite tables for `sources`, `documents`, and `skill_examples`, and an index directory under the Skill Forge home. The design should use those existing pieces instead of adding a new storage backend.

## Goals / Non-Goals

**Goals:**

- Add `skill-forge search "<query>"`.
- Build and persist a TF-IDF index from local normalized corpus content and SQLite metadata.
- Rebuild the index automatically when no usable index exists or corpus metadata has changed.
- Return top-k ranked search results with name/title, source, platform, summary, and score.
- Apply deterministic ranking boosts for authority, content completeness, freshness, and optional platform match.
- Provide clear user feedback when the corpus is empty.
- Keep indexing and ranking testable without network access.

**Non-Goals:**

- No vector database or embedding model.
- No LLM reranking.
- No automatic `skill-forge update` from `search`.
- No integration into `create` in this change.
- No advanced pattern extraction.
- No fuzzy command aliases beyond `search`.

## Decisions

1. Use TF-IDF over normalized corpus text plus metadata fields.

   Rationale: The design document explicitly calls for scikit-learn TF-IDF as the MVP retrieval mechanism. Normalized files contain richer text than summaries alone, while metadata fields improve short-query matching.

   Alternative considered: SQLite `LIKE` search. That is simpler, but ranking quality and top-k relevance are weaker.

2. Persist the index as files under the existing index directory.

   Rationale: The workspace already creates `~/.skill-forge/index`. Persisting `tfidf.pkl` and metadata avoids rebuilding on every search and matches the design document's local data layout.

   Alternative considered: Rebuild every time. That is acceptable for tiny corpora but scales poorly and makes search latency unpredictable.

3. Detect stale indexes using a corpus signature.

   Rationale: Search should work without a separate manual indexing command. A signature derived from document ids, hashes, normalized paths, and update timestamps is deterministic and easy to test.

   Alternative considered: Depend on `skill-forge update` to rebuild the index. That would couple two commands and make stale search behavior easier to miss.

4. Keep ranking as a transparent weighted score.

   Rationale: TF-IDF relevance should dominate, but source authority, completeness, freshness, and platform hints are useful tie-breakers. Simple boost functions are deterministic and easy to explain.

   Alternative considered: Learn ranking weights or add reranking. That is overkill for the MVP and would require more training/evaluation data.

5. Return empty-state output instead of treating an empty corpus as an error.

   Rationale: A user may run `search` before `update`. The command should explain that no local corpus exists and suggest running `skill-forge update`, but it does not need to fail as an exceptional condition.

   Alternative considered: Return non-zero on empty corpus. That makes shell automation stricter but is less friendly for a discovery command.

## Risks / Trade-offs

- TF-IDF quality depends on normalized content quality. -> Include summaries and metadata in indexed text, and keep ranking boosts small and deterministic.
- Pickle index files can become incompatible across library versions. -> Rebuild automatically when loading fails.
- Stale detection can miss changes outside SQLite metadata. -> Include normalized file path and content hash in the corpus signature.
- Very large normalized files may increase memory usage. -> MVP reads full normalized text; future changes can add chunking if needed.
- Ranking weights may not match user expectations. -> Keep weights centralized and covered by tests so they can be tuned later.

## Migration Plan

This change is additive. Existing update, create, validate, install, and draft commands remain unchanged. Search creates or replaces index files under `~/.skill-forge/index`.

Rollback removes the search command, retrieval modules, and index files. SQLite corpus data and generated Skills remain unaffected.

## Open Questions

- Should future `skill-forge update` rebuild the TF-IDF index automatically after corpus refresh?
- Should generation use top search results by default, or require an explicit flag once retrieval is integrated into `create`?
