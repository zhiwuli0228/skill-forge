from pathlib import Path

from skill_forge.models.collection import (
    CollectionRecord,
    CollectionState,
    ScoreDimension,
    ScoreSnapshot,
    build_collection_record,
)
from skill_forge.storage.collection_store import CollectionStore


def _make_store(tmp_path: Path) -> CollectionStore:
    return CollectionStore(tmp_path / "collections")


def test_collection_record_defaults_to_candidate() -> None:
    record = build_collection_record(
        skill_id="test-skill",
        package_name="test-skill",
        origin_type="generated",
    )

    assert record.collection_state == CollectionState.CANDIDATE
    assert record.collection_score == 0.0
    assert record.promotion_score == 0.0
    assert record.manual_override is False
    assert record.created_at != ""
    assert record.updated_at != ""


def test_collection_record_is_curated_or_better() -> None:
    candidate = build_collection_record(skill_id="a", package_name="a", origin_type="generated")
    curated = build_collection_record(skill_id="b", package_name="b", origin_type="generated", collection_state=CollectionState.CURATED)
    promoted = build_collection_record(skill_id="c", package_name="c", origin_type="generated", collection_state=CollectionState.PROMOTED)
    rejected = build_collection_record(skill_id="d", package_name="d", origin_type="generated", collection_state=CollectionState.REJECTED)

    assert not candidate.is_curated_or_better
    assert curated.is_curated_or_better
    assert promoted.is_curated_or_better
    assert not rejected.is_curated_or_better
    assert promoted.is_promoted
    assert not curated.is_promoted


def test_store_write_and_read_record(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    record = build_collection_record(
        skill_id="test-skill",
        package_name="test-skill",
        origin_type="generated",
        origin_reference="some-bundle",
        rationale="Initial import",
    )

    path = store.write_record(record)
    assert path.is_file()

    loaded = store.read_record("test-skill")
    assert loaded is not None
    assert loaded.skill_id == "test-skill"
    assert loaded.package_name == "test-skill"
    assert loaded.origin_type == "generated"
    assert loaded.origin_reference == "some-bundle"
    assert loaded.rationale == "Initial import"
    assert loaded.collection_state == CollectionState.CANDIDATE


def test_store_read_missing_record_returns_none(tmp_path: Path) -> None:
    store = _make_store(tmp_path)

    assert store.read_record("nonexistent") is None


def test_store_list_records_returns_sorted(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    store.write_record(build_collection_record(skill_id="beta", package_name="beta", origin_type="generated"))
    store.write_record(build_collection_record(skill_id="alpha", package_name="alpha", origin_type="adopted"))

    records = store.list_records()

    assert [r.skill_id for r in records] == ["alpha", "beta"]


def test_store_update_state(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    store.write_record(build_collection_record(skill_id="test-skill", package_name="test-skill", origin_type="generated"))

    updated = store.update_state("test-skill", state=CollectionState.CURATED, rationale="Good quality")

    assert updated is not None
    assert updated.collection_state == CollectionState.CURATED
    assert updated.manual_override is True
    assert updated.rationale == "Good quality"

    loaded = store.read_record("test-skill")
    assert loaded is not None
    assert loaded.collection_state == CollectionState.CURATED


def test_store_update_state_missing_returns_none(tmp_path: Path) -> None:
    store = _make_store(tmp_path)

    assert store.update_state("nonexistent", state=CollectionState.CURATED) is None


def test_store_delete_record(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    store.write_record(build_collection_record(skill_id="test-skill", package_name="test-skill", origin_type="generated"))

    assert store.delete_record("test-skill") is True
    assert store.read_record("test-skill") is None
    assert store.exists("test-skill") is False


def test_store_delete_missing_returns_false(tmp_path: Path) -> None:
    store = _make_store(tmp_path)

    assert store.delete_record("nonexistent") is False


def test_store_write_and_read_snapshot(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    snapshot = ScoreSnapshot(
        skill_id="test-skill",
        snapshot_at="2026-06-07T00:00:00Z",
        structure_score=0.8,
        quality_score=0.9,
        eval_score=1.0,
        lifecycle_score=0.7,
        final_collection_score=0.85,
        final_promotion_score=0.80,
        dimensions=[
            ScoreDimension(name="structure", score=0.8, evidence="complete"),
            ScoreDimension(name="quality", score=0.9, evidence="good"),
        ],
    )

    store.write_snapshot(snapshot)
    loaded = store.read_snapshot("test-skill")

    assert loaded is not None
    assert loaded.skill_id == "test-skill"
    assert loaded.final_collection_score == 0.85
    assert len(loaded.dimensions) == 2


def test_store_read_missing_snapshot_returns_none(tmp_path: Path) -> None:
    store = _make_store(tmp_path)

    assert store.read_snapshot("nonexistent") is None


def test_store_list_by_state(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    store.write_record(build_collection_record(skill_id="a", package_name="a", origin_type="generated"))
    store.write_record(build_collection_record(skill_id="b", package_name="b", origin_type="generated", collection_state=CollectionState.CURATED))
    store.write_record(build_collection_record(skill_id="c", package_name="c", origin_type="generated", collection_state=CollectionState.PROMOTED))

    promoted = store.list_by_state(CollectionState.PROMOTED)
    curated = store.list_by_state(CollectionState.CURATED)
    candidates = store.list_by_state(CollectionState.CANDIDATE)

    assert [r.skill_id for r in promoted] == ["c"]
    assert [r.skill_id for r in curated] == ["b"]
    assert [r.skill_id for r in candidates] == ["a"]


def test_store_handles_corrupted_manifest_gracefully(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    store.ensure_directories()
    (store.manifests_dir / "bad.json").write_text("not json{", encoding="utf-8")

    records = store.list_records()
    assert records == []

    assert store.read_record("bad") is None


def test_store_ensures_directories_on_write(tmp_path: Path) -> None:
    store = _make_store(tmp_path)
    assert not store.collections_dir.exists()

    store.write_record(build_collection_record(skill_id="test", package_name="test", origin_type="generated"))

    assert store.manifests_dir.exists()
    assert store.snapshots_dir.exists()
    assert store.indexes_dir.exists()
