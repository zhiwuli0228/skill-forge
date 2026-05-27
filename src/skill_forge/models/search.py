from pathlib import Path

from pydantic import BaseModel, ConfigDict


class CorpusDocument(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    document_id: int
    example_id: int | None = None
    title: str
    source_name: str
    authority_level: str
    platform: str | None = None
    summary: str
    normalized_path: Path
    content_hash: str
    updated_at: str | None = None
    content: str = ""

    @property
    def indexed_text(self) -> str:
        return "\n".join(
            part
            for part in (
                self.title,
                self.source_name,
                self.platform or "",
                self.summary,
                self.authority_level,
                self.content,
            )
            if part
        )

    @property
    def completeness(self) -> float:
        score = 0.0
        if self.summary:
            score += 0.35
        if self.content:
            score += 0.45
        if self.platform and self.platform != "unknown":
            score += 0.10
        if len(self.content) >= 300:
            score += 0.10
        return min(score, 1.0)


class SearchResult(BaseModel):
    title: str
    source_name: str
    platform: str | None = None
    summary: str
    score: float
    relevance_score: float
    authority_boost: float
    completeness_boost: float
    freshness_boost: float
    platform_boost: float
    normalized_path: Path
    retrieval_mode: str = "tfidf"
    rerank_score: float | None = None
    rerank_error: str | None = None

    @property
    def score_explanation(self) -> str:
        rerank = f", rerank={self.rerank_score:.3f}" if self.rerank_score is not None else ""
        return (
            f"relevance={self.relevance_score:.3f}, "
            f"authority={self.authority_boost:.3f}, "
            f"completeness={self.completeness_boost:.3f}, "
            f"freshness={self.freshness_boost:.3f}, "
            f"platform={self.platform_boost:.3f}, "
            f"final={self.score:.3f}"
            f"{rerank}"
        )
