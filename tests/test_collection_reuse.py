from pathlib import Path

from skill_forge.models.collection import CollectionState, build_collection_record
from skill_forge.models.search import SearchResult
from skill_forge.retrieval.generation_integration import (
    PromotedEvidencePreference,
    PromotedReferenceSelector,
)
from skill_forge.storage.collection_store import CollectionStore


def _make_result(title: str, relevance: float = 0.5, quality: float = 0.8) -> SearchResult:
    return SearchResult(
        document_id=1,
        title=title,
        source_name="test",
        summary="test",
        score=relevance,
        relevance_score=relevance,
        quality_score=quality,
        authority_boost=0.0,
        completeness_boost=0.0,
        freshness_boost=0.0,
        platform_boost=0.0,
        normalized_path=Path("/test"),
    )


def test_promoted_reference_selector_prefers_promoted(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Promoted Skill", package_name="Promoted Skill", origin_type="generated", collection_state=CollectionState.PROMOTED))
    store.write_record(build_collection_record(skill_id="Normal Skill", package_name="Normal Skill", origin_type="generated"))

    selector = PromotedReferenceSelector(store)
    candidates = [_make_result("Normal Skill"), _make_result("Promoted Skill")]

    preferred = selector.prefer_promoted(candidates)

    assert preferred[0].title == "Promoted Skill"
    assert preferred[0].collection_state == "promoted"
    assert preferred[1].title == "Normal Skill"


def test_promoted_reference_selector_prefers_curated_over_normal(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Curated Skill", package_name="Curated Skill", origin_type="generated", collection_state=CollectionState.CURATED))

    selector = PromotedReferenceSelector(store)
    candidates = [_make_result("Other Skill"), _make_result("Curated Skill")]

    preferred = selector.prefer_promoted(candidates)

    assert preferred[0].title == "Curated Skill"
    assert preferred[0].collection_state == "curated"


def test_promoted_reference_selector_respects_relevance_threshold(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Promoted Skill", package_name="Promoted Skill", origin_type="generated", collection_state=CollectionState.PROMOTED))

    selector = PromotedReferenceSelector(store)
    candidates = [_make_result("Promoted Skill", relevance=0.01)]

    preferred = selector.prefer_promoted(candidates, relevance_threshold=0.1)

    assert len(preferred) == 1
    assert preferred[0].title == "Promoted Skill"


def test_promoted_reference_selector_respects_quality_threshold(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Promoted Skill", package_name="Promoted Skill", origin_type="generated", collection_state=CollectionState.PROMOTED))

    selector = PromotedReferenceSelector(store)
    candidates = [_make_result("Promoted Skill", quality=0.3)]

    preferred = selector.prefer_promoted(candidates, quality_threshold=0.5)

    assert len(preferred) == 1


def test_promoted_reference_selector_returns_none_when_empty(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    selector = PromotedReferenceSelector(store)

    result = selector.select_reference([])

    assert result is None


def test_promoted_reference_selector_selects_first_promoted(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="Promoted Skill", package_name="Promoted Skill", origin_type="generated", collection_state=CollectionState.PROMOTED))

    selector = PromotedReferenceSelector(store)
    candidates = [_make_result("Normal Skill"), _make_result("Promoted Skill")]

    result = selector.select_reference(candidates)

    assert result is not None
    assert result.title == "Promoted Skill"


def test_promoted_reference_selector_falls_back_to_normal(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    selector = PromotedReferenceSelector(store)
    candidates = [_make_result("Normal Skill")]

    result = selector.select_reference(candidates)

    assert result is not None
    assert result.title == "Normal Skill"


def test_evidence_preference_weights_promoted_higher(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="promoted-skill", package_name="promoted-skill", origin_type="generated", collection_state=CollectionState.PROMOTED))
    store.write_record(build_collection_record(skill_id="curated-skill", package_name="curated-skill", origin_type="generated", collection_state=CollectionState.CURATED))

    preference = PromotedEvidencePreference(store)
    weighted = preference.weight_packages(["normal-skill", "promoted-skill", "curated-skill"])

    weights = dict(weighted)
    assert weights["promoted-skill"] == 2.0
    assert weights["curated-skill"] == 1.5
    assert weights["normal-skill"] == 1.0


def test_evidence_preference_sorts_by_preference(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    store.write_record(build_collection_record(skill_id="promoted-skill", package_name="promoted-skill", origin_type="generated", collection_state=CollectionState.PROMOTED))
    store.write_record(build_collection_record(skill_id="curated-skill", package_name="curated-skill", origin_type="generated", collection_state=CollectionState.CURATED))

    preference = PromotedEvidencePreference(store)
    sorted_names = preference.sort_by_preference(["normal-skill", "curated-skill", "promoted-skill"])

    assert sorted_names == ["promoted-skill", "curated-skill", "normal-skill"]


def test_evidence_preference_handles_no_collection_records(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    preference = PromotedEvidencePreference(store)

    sorted_names = preference.sort_by_preference(["skill-a", "skill-b"])

    assert sorted_names == ["skill-a", "skill-b"]
