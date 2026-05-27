from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from skill_forge.models.search import SearchResult


class RerankError(RuntimeError):
    pass


class SearchReranker(Protocol):
    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        """Return the same results in reranked order."""


@dataclass(frozen=True)
class LexicalReranker:
    """Dependency-free reranker based on query term coverage in result metadata."""

    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        terms = _terms(query)
        if not terms:
            return [_with_rerank(result, result.score) for result in results]

        scored: list[tuple[SearchResult, float]] = []
        for result in results:
            haystack = " ".join([result.title, result.source_name, result.platform or "", result.summary]).casefold()
            matched = sum(1 for term in terms if term in haystack)
            coverage = matched / len(terms)
            title_hits = sum(1 for term in terms if term in result.title.casefold()) / len(terms)
            rerank_score = round((coverage * 0.7) + (title_hits * 0.2) + (result.score * 0.1), 6)
            scored.append((_with_rerank(result, rerank_score), rerank_score))

        scored.sort(key=lambda item: (-item[1], -item[0].score, item[0].title, item[0].source_name))
        return [result for result, _score in scored]


def build_reranker(provider: str) -> SearchReranker:
    if provider == "lexical":
        return LexicalReranker()
    raise RerankError(f"Unsupported rerank provider: {provider}")


def _with_rerank(result: SearchResult, rerank_score: float) -> SearchResult:
    return result.model_copy(update={"retrieval_mode": "tfidf+rerank", "rerank_score": round(rerank_score, 6)})


def _terms(query: str) -> list[str]:
    return list(dict.fromkeys(term.casefold() for term in re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]*", query)))
