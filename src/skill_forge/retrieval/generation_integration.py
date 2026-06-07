from __future__ import annotations

from pathlib import Path

from skill_forge.models.collection import CollectionState
from skill_forge.models.search import SearchResult
from skill_forge.storage.collection_store import CollectionStore


class PromotedReferenceSelector:
    """Prefers promoted Skills as references when relevance and quality gates still pass."""

    def __init__(self, store: CollectionStore) -> None:
        self._store = store

    def prefer_promoted(
        self,
        candidates: list[SearchResult],
        *,
        relevance_threshold: float = 0.0,
        quality_threshold: float = 0.0,
    ) -> list[SearchResult]:
        if not candidates:
            return candidates

        enriched: list[SearchResult] = []
        for candidate in candidates:
            record = self._store.read_record(candidate.title)
            state = record.collection_state.value if record is not None else None
            enriched.append(candidate.model_copy(update={"collection_state": state}))

        passing = [
            c for c in enriched
            if c.relevance_score >= relevance_threshold
            and (c.quality_score is None or c.quality_score >= quality_threshold)
        ]
        if not passing:
            return candidates

        promoted = [c for c in passing if c.collection_state == CollectionState.PROMOTED.value]
        curated = [c for c in passing if c.collection_state == CollectionState.CURATED.value]
        others = [c for c in passing if c.collection_state not in (CollectionState.PROMOTED.value, CollectionState.CURATED.value)]

        return promoted + curated + others

    def select_reference(
        self,
        candidates: list[SearchResult],
        *,
        relevance_threshold: float = 0.0,
        quality_threshold: float = 0.0,
    ) -> SearchResult | None:
        preferred = self.prefer_promoted(
            candidates,
            relevance_threshold=relevance_threshold,
            quality_threshold=quality_threshold,
        )
        return preferred[0] if preferred else None


class PromotedEvidencePreference:
    """Weights promoted Skills higher when collecting experience evidence."""

    def __init__(self, store: CollectionStore) -> None:
        self._store = store

    def weight_packages(
        self,
        package_names: list[str],
    ) -> list[tuple[str, float]]:
        weighted: list[tuple[str, float]] = []
        for name in package_names:
            record = self._store.read_record(name)
            weight = 1.0
            if record is not None:
                if record.collection_state == CollectionState.PROMOTED:
                    weight = 2.0
                elif record.collection_state == CollectionState.CURATED:
                    weight = 1.5
            weighted.append((name, weight))
        return weighted

    def sort_by_preference(
        self,
        package_names: list[str],
    ) -> list[str]:
        weighted = self.weight_packages(package_names)
        return [name for name, _ in sorted(weighted, key=lambda x: -x[1])]
