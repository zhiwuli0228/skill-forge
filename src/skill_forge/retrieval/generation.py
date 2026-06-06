from pathlib import Path
import re

from pydantic import BaseModel, Field

from skill_forge.models.search import SearchResult
from skill_forge.retrieval.retriever import CorpusRetriever


class GenerationRetrievalContext(BaseModel):
    used: bool = False
    skipped_reason: str | None = None
    source_names: list[str] = Field(default_factory=list)
    workflow_patterns: list[str] = Field(default_factory=list)
    constraint_patterns: list[str] = Field(default_factory=list)
    quality_gate_patterns: list[str] = Field(default_factory=list)


class GenerationRetrievalAugmenter:
    def __init__(
        self,
        retriever: CorpusRetriever,
        *,
        top_k: int = 3,
        min_corpus_documents: int = 10,
        min_relevance_score: float = 0.05,
        min_quality_score: float = 0.5,
        max_patterns_per_kind: int = 5,
    ) -> None:
        self._retriever = retriever
        self._top_k = top_k
        self._min_corpus_documents = min_corpus_documents
        self._min_relevance_score = min_relevance_score
        self._min_quality_score = min_quality_score
        self._max_patterns_per_kind = max_patterns_per_kind

    def build_context(self, query: str, *, platform: str | None = None) -> GenerationRetrievalContext:
        index = self._retriever.indexer.load_or_build()
        if index is None or not index.documents:
            return GenerationRetrievalContext(skipped_reason="empty-corpus")
        if len(index.documents) < self._min_corpus_documents:
            return GenerationRetrievalContext(skipped_reason="insufficient-corpus")

        results = self._retriever._search_index(
            index,
            query,
            top_k=max(self._top_k * 3, self._top_k),
            platform=platform,
        )
        candidates = [
            result
            for result in results
            if result.relevance_score >= self._min_relevance_score
            and (result.quality_score is None or result.quality_score >= self._min_quality_score)
        ][: self._top_k]
        if not candidates:
            return GenerationRetrievalContext(skipped_reason="below-quality-threshold")

        context = GenerationRetrievalContext(source_names=_dedupe([_source_label(result) for result in candidates]))
        for result in candidates:
            content = _read_result_content(result)
            context.workflow_patterns.extend(_extract_section_items(content, ("Workflow",)))
            context.constraint_patterns.extend(_extract_section_items(content, ("Constraints",)))
            context.quality_gate_patterns.extend(_extract_section_items(content, ("Quality gates", "Quality gate")))

        context.workflow_patterns = _dedupe(context.workflow_patterns)[: self._max_patterns_per_kind]
        context.constraint_patterns = _dedupe(context.constraint_patterns)[: self._max_patterns_per_kind]
        context.quality_gate_patterns = _dedupe(context.quality_gate_patterns)[: self._max_patterns_per_kind]
        context.used = any((context.workflow_patterns, context.constraint_patterns, context.quality_gate_patterns))
        if not context.used:
            context.skipped_reason = "no-extractable-patterns"
        return context


def _source_label(result: SearchResult) -> str:
    if result.example_id is not None:
        return f"{result.title}#{result.example_id}"
    return result.title


def _read_result_content(result: SearchResult) -> str:
    try:
        return Path(result.normalized_path).read_text(encoding="utf-8")
    except OSError:
        return ""


def _extract_section_items(content: str, section_names: tuple[str, ...]) -> list[str]:
    section = _extract_section(content, section_names)
    if not section:
        return []
    items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.+)$", stripped)
        if match:
            items.append(match.group(1).strip())
    return [item for item in items if item]


def _extract_section(content: str, section_names: tuple[str, ...]) -> str:
    lines = content.splitlines()
    collecting = False
    collected: list[str] = []
    start_level = 0
    wanted = {name.lower() for name in section_names}
    for line in lines:
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip().lower()
            if collecting and level <= start_level:
                break
            if title in wanted:
                collecting = True
                start_level = level
                continue
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        normalized = " ".join(item.strip().split())
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        unique.append(normalized)
    return unique
