from sklearn.metrics.pairwise import cosine_similarity

from skill_forge.models.search import SearchResult
from skill_forge.retrieval.indexer import SearchIndex, TfidfIndexer
from skill_forge.retrieval.ranker import RankingEngine
from skill_forge.retrieval.reranker import RerankError, SearchReranker


class SearchFallbackWarning(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class SearchResponse:
    def __init__(self, results: list[SearchResult], *, retrieval_mode: str, warning: SearchFallbackWarning | None = None) -> None:
        self.results = results
        self.retrieval_mode = retrieval_mode
        self.warning = warning


class CorpusRetriever:
    def __init__(self, indexer: TfidfIndexer, ranker: RankingEngine | None = None) -> None:
        self.indexer = indexer
        self.ranker = ranker or RankingEngine()

    def search(self, query: str, *, top_k: int, platform: str | None = None) -> list[SearchResult]:
        return self.search_with_metadata(query, top_k=top_k, platform=platform).results

    def search_with_metadata(
        self,
        query: str,
        *,
        top_k: int,
        platform: str | None = None,
        reranker: SearchReranker | None = None,
        rerank_candidate_multiplier: int = 3,
    ) -> SearchResponse:
        index = self.indexer.load_or_build()
        if index is None:
            return SearchResponse([], retrieval_mode="tfidf")
        limit = max(top_k, 1)
        candidates = self._search_index(
            index,
            query,
            top_k=limit * max(rerank_candidate_multiplier, 1),
            platform=platform,
        )
        if reranker is None:
            return SearchResponse(candidates[:limit], retrieval_mode="tfidf")
        try:
            reranked = reranker.rerank(query, candidates)
        except (RerankError, RuntimeError, ValueError) as exc:
            warning = SearchFallbackWarning(f"Rerank failed, falling back to TF-IDF: {exc}")
            fallback = [result.model_copy(update={"retrieval_mode": "tfidf", "rerank_error": str(exc)}) for result in candidates[:limit]]
            return SearchResponse(fallback, retrieval_mode="tfidf", warning=warning)
        return SearchResponse(reranked[:limit], retrieval_mode="tfidf+rerank")

    def _search_index(
        self,
        index: SearchIndex,
        query: str,
        *,
        top_k: int,
        platform: str | None,
    ) -> list[SearchResult]:
        query_vector = index.vectorizer.transform([query])
        relevance_scores = cosine_similarity(query_vector, index.matrix).flatten()
        results: list[SearchResult] = []

        for document, relevance_score in zip(index.documents, relevance_scores, strict=True):
            if relevance_score <= 0:
                continue
            score, authority, completeness, freshness, platform_boost = self.ranker.score(
                document,
                float(relevance_score),
                platform=platform,
            )
            results.append(
                SearchResult(
                    document_id=document.document_id,
                    example_id=document.example_id,
                    title=document.title,
                    source_name=document.source_name,
                    source_url=document.source_url,
                    document_url=document.document_url,
                    platform=document.platform,
                    summary=document.summary,
                    quality_score=document.quality_score,
                    score=score,
                    relevance_score=round(float(relevance_score), 6),
                    authority_boost=authority,
                    completeness_boost=completeness,
                    freshness_boost=freshness,
                    platform_boost=platform_boost,
                    normalized_path=document.normalized_path,
                )
            )

        results.sort(key=lambda result: (-result.score, result.title, result.source_name))
        return results[:top_k]
