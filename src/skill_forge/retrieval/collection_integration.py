from __future__ import annotations

from skill_forge.models.collection import CollectionState
from skill_forge.models.search import SearchResult
from skill_forge.storage.collection_store import CollectionStore


PROMOTED_BOOST_DEFAULT = 0.10
CURATED_BOOST_DEFAULT = 0.05


class CollectionSearchFilter:
    def __init__(self, store: CollectionStore) -> None:
        self._store = store

    def apply(
        self,
        results: list[SearchResult],
        *,
        collection_filter: CollectionState | None = None,
        promoted_boost: float = PROMOTED_BOOST_DEFAULT,
        curated_boost: float = CURATED_BOOST_DEFAULT,
    ) -> list[SearchResult]:
        enriched = self._enrich_with_collection(results)

        if collection_filter is not None:
            enriched = [r for r in enriched if r.collection_state == collection_filter.value]

        if promoted_boost > 0 or curated_boost > 0:
            enriched = self._apply_boost(enriched, promoted_boost, curated_boost)

        return sorted(enriched, key=lambda r: (-r.score, r.title, r.source_name))

    def _enrich_with_collection(self, results: list[SearchResult]) -> list[SearchResult]:
        enriched: list[SearchResult] = []
        for result in results:
            record = self._store.read_record(result.title)
            if record is not None:
                result = result.model_copy(update={
                    "collection_state": record.collection_state.value,
                })
            enriched.append(result)
        return enriched

    def _apply_boost(
        self,
        results: list[SearchResult],
        promoted_boost: float,
        curated_boost: float,
    ) -> list[SearchResult]:
        boosted: list[SearchResult] = []
        for result in results:
            boost = 0.0
            if result.collection_state == CollectionState.PROMOTED.value:
                boost = promoted_boost
            elif result.collection_state == CollectionState.CURATED.value:
                boost = curated_boost
            if boost > 0:
                result = result.model_copy(update={
                    "score": result.score + boost,
                    "collection_boost": boost,
                })
            boosted.append(result)
        return boosted
