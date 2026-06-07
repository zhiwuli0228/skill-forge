from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from skill_forge.models.search import SearchResult
from skill_forge.retrieval.indexer import TfidfIndexer, TfidfIndexStore
from skill_forge.retrieval.retriever import CorpusRetriever
from skill_forge.storage.corpus_reader import CorpusReader


class SemanticIndexMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    index_version: str = "tfidf-semantic-v1"
    provider: str = "local-tfidf"
    embedding_dim: int = 0
    last_built_at: str | None = None
    document_count: int = 0
    fallback_mode: str = "tfidf"


class SimilarityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_title: str
    target_title: str
    similarity_score: float
    source_document_id: int | None = None
    target_document_id: int | None = None


class SemanticSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results: list[SearchResult]
    retrieval_mode: str = "semantic-tfidf"
    index_metadata: SemanticIndexMetadata | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None


class SemanticRetriever:
    """Optional semantic retrieval using local TF-IDF with enhanced similarity."""

    def __init__(self, indexer: TfidfIndexer) -> None:
        self._indexer = indexer

    @property
    def indexer(self) -> TfidfIndexer:
        return self._indexer

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        platform: str | None = None,
    ) -> SemanticSearchResult:
        index = self._indexer.load_or_build()
        if index is None:
            return SemanticSearchResult(
                results=[],
                retrieval_mode="semantic-tfidf",
                fallback_used=True,
                fallback_reason="empty-corpus",
            )

        retriever = CorpusRetriever(self._indexer)
        results = retriever.search(query, top_k=top_k, platform=platform)

        metadata = SemanticIndexMetadata(
            embedding_dim=index.matrix.shape[1] if index.matrix is not None else 0,
            document_count=len(index.documents),
        )

        return SemanticSearchResult(
            results=results,
            retrieval_mode="semantic-tfidf",
            index_metadata=metadata,
        )

    def find_similar(
        self,
        title: str,
        *,
        top_k: int = 5,
        min_similarity: float = 0.1,
    ) -> list[SimilarityResult]:
        from sklearn.metrics.pairwise import cosine_similarity

        index = self._indexer.load_or_build()
        if index is None:
            return []

        target_idx = None
        for i, doc in enumerate(index.documents):
            if doc.title == title:
                target_idx = i
                break
        if target_idx is None:
            return []

        target_vector = index.matrix[target_idx]
        similarities = cosine_similarity(target_vector, index.matrix).flatten()

        results: list[SimilarityResult] = []
        for i, (doc, sim) in enumerate(zip(index.documents, similarities)):
            if i == target_idx or sim < min_similarity:
                continue
            results.append(
                SimilarityResult(
                    source_title=title,
                    target_title=doc.title,
                    similarity_score=round(float(sim), 6),
                    source_document_id=index.documents[target_idx].document_id,
                    target_document_id=doc.document_id,
                )
            )

        results.sort(key=lambda r: -r.similarity_score)
        return results[:top_k]

    def detect_duplicates(
        self,
        *,
        threshold: float = 0.8,
    ) -> list[SimilarityResult]:
        from sklearn.metrics.pairwise import cosine_similarity

        index = self._indexer.load_or_build()
        if index is None or len(index.documents) < 2:
            return []

        sim_matrix = cosine_similarity(index.matrix)
        duplicates: list[SimilarityResult] = []

        for i in range(len(index.documents)):
            for j in range(i + 1, len(index.documents)):
                sim = float(sim_matrix[i, j])
                if sim >= threshold:
                    duplicates.append(
                        SimilarityResult(
                            source_title=index.documents[i].title,
                            target_title=index.documents[j].title,
                            similarity_score=round(sim, 6),
                            source_document_id=index.documents[i].document_id,
                            target_document_id=index.documents[j].document_id,
                        )
                    )

        duplicates.sort(key=lambda r: -r.similarity_score)
        return duplicates

    def get_metadata(self) -> SemanticIndexMetadata | None:
        index = self._indexer.load_or_build()
        if index is None:
            return None
        return SemanticIndexMetadata(
            embedding_dim=index.matrix.shape[1] if index.matrix is not None else 0,
            document_count=len(index.documents),
        )
