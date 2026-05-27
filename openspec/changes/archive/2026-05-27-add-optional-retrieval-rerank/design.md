## Context

Search currently builds a TF-IDF index from local corpus documents, computes final scores with deterministic ranking boosts, sorts by final score, and returns compact `SearchResult` objects. The previous research-quality change exposed ranking component explanations but intentionally did not alter ranking behavior.

This change adds a second-stage reranking hook. The first implementation should remain local and dependency-free so `search --rerank` works offline and does not require model downloads.

## Goals / Non-Goals

**Goals:**

- Keep TF-IDF as the default retrieval and ranking path.
- Add a reranker interface that can be replaced later.
- Provide one built-in offline reranker.
- Allow `skill-forge search --rerank` to opt in per command.
- Add config controls for rerank availability and default opt-in.
- Clearly show whether output used `tfidf` or `tfidf+rerank`.
- Fall back to TF-IDF order if rerank fails.

**Non-Goals:**

- Do not add embedding models.
- Do not add vector databases.
- Do not require network access.
- Do not make `create` depend on rerank.
- Do not change TF-IDF index construction.

## Decisions

1. Implement rerank as a post-processing step over TF-IDF candidates.

   Rationale: The corpus index and first-stage retrieval stay unchanged. Later semantic rerankers can plug into the same boundary.

2. Fetch a wider candidate set before reranking.

   Rationale: Rerank needs more than `top_k` candidates to change ordering. Use a small deterministic multiplier rather than scanning every result.

3. Add a dependency-free lexical reranker.

   Rationale: It keeps local-first behavior and provides testable behavior without adding heavyweight dependencies.

4. Record `retrieval_mode` and `rerank_score` on search results.

   Rationale: CLI can label output and tests can verify when rerank is active.

5. Fall back on rerank failure.

   Rationale: Optional rerank should not make search unusable when a configured reranker fails.

## Risks / Trade-offs

- Lexical rerank is not semantic rerank -> Mitigation: name it as local lexical rerank and keep the interface extensible.
- Rerank can reorder results unexpectedly -> Mitigation: it is opt-in and output labels the mode.
- Wider candidate fetching can add cost -> Mitigation: use a bounded candidate multiplier.
- Fallback can hide broken reranker implementations -> Mitigation: print a clear warning when fallback occurs.

## Migration Plan

No migration is required. Existing configs load with rerank disabled by default. Existing `search` commands keep the same behavior unless users pass `--rerank` or explicitly enable default reranking in config.
