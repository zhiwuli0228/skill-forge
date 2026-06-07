from pathlib import Path

from skill_forge.lifecycle.scoring import (
    CURATED_THRESHOLD,
    PROMOTION_THRESHOLD,
    SCORE_VERSION,
    ScoringConfig,
    ScoringInputs,
    compute_scores,
    suggested_state,
)
from skill_forge.models.collection import CollectionState, ScoreSnapshot
from skill_forge.storage.collection_store import CollectionStore


def _full_inputs() -> ScoringInputs:
    inputs = ScoringInputs()
    inputs.has_skill_md = True
    inputs.has_frontmatter = True
    inputs.has_required_sections = True
    inputs.quality_score = 95
    inputs.quality_status = "valid"
    inputs.content_quality_workflow = 0.9
    inputs.content_quality_constraint = 0.85
    inputs.content_quality_gate = 0.88
    inputs.eval_total = 3
    inputs.eval_passed = 3
    inputs.eval_failed = 0
    inputs.lifecycle_state = "healthy"
    inputs.has_provenance = True
    inputs.origin_type = "blueprint-generated"
    inputs.has_applied_experience = True
    inputs.reuse_count = 2
    return inputs


def test_scoring_deterministic_same_inputs_same_output() -> None:
    inputs = _full_inputs()

    first = compute_scores(inputs)
    second = compute_scores(inputs)

    assert first.final_collection_score == second.final_collection_score
    assert first.final_promotion_score == second.final_promotion_score
    assert first.score_version == second.score_version
    for d1, d2 in zip(first.dimensions, second.dimensions):
        assert d1.score == d2.score
        assert d1.evidence == d2.evidence


def test_scoring_version_is_v1() -> None:
    snapshot = compute_scores(_full_inputs())

    assert snapshot.score_version == SCORE_VERSION
    assert snapshot.score_version == "v1"


def test_scoring_full_evidence_produces_high_scores() -> None:
    snapshot = compute_scores(_full_inputs())

    assert snapshot.structure_score > 0.9
    assert snapshot.quality_score > 0.9
    assert snapshot.eval_score == 1.0
    assert snapshot.lifecycle_score == 1.0
    assert snapshot.provenance_score > 0.9
    assert snapshot.reuse_score > 0.0
    assert snapshot.final_collection_score > 0.7
    assert snapshot.final_promotion_score > 0.7


def test_scoring_missing_all_signals_produces_zero() -> None:
    inputs = ScoringInputs()

    snapshot = compute_scores(inputs)

    assert snapshot.structure_score == 0.0
    assert snapshot.quality_score == 0.0
    assert snapshot.eval_score == 0.0
    assert snapshot.lifecycle_score == 0.0
    assert snapshot.provenance_score == 0.0
    assert snapshot.reuse_score == 0.0
    assert snapshot.final_collection_score == 0.0
    assert snapshot.final_promotion_score == 0.0


def test_scoring_missing_eval_produces_zero_eval_score() -> None:
    inputs = _full_inputs()
    inputs.eval_total = None
    inputs.eval_passed = None

    snapshot = compute_scores(inputs)

    assert snapshot.eval_score == 0.0


def test_scoring_failing_eval_reduces_score() -> None:
    passing = _full_inputs()
    passing.eval_total = 5
    passing.eval_passed = 5
    passing.eval_failed = 0

    failing = _full_inputs()
    failing.eval_total = 5
    failing.eval_passed = 3
    failing.eval_failed = 2

    passing_snap = compute_scores(passing)
    failing_snap = compute_scores(failing)

    assert passing_snap.eval_score > failing_snap.eval_score


def test_scoring_quality_score_normalizes_to_0_1() -> None:
    inputs = _full_inputs()
    inputs.quality_score = 50

    snapshot = compute_scores(inputs)

    assert 0.4 <= snapshot.quality_score <= 0.7


def test_scoring_structure_requires_all_parts() -> None:
    no_md = _full_inputs()
    no_md.has_skill_md = False

    no_front = _full_inputs()
    no_front.has_frontmatter = False

    no_sections = _full_inputs()
    no_sections.has_required_sections = False

    assert compute_scores(no_md).structure_score < compute_scores(_full_inputs()).structure_score
    assert compute_scores(no_front).structure_score < compute_scores(_full_inputs()).structure_score
    assert compute_scores(no_sections).structure_score < compute_scores(_full_inputs()).structure_score


def test_scoring_lifecycle_healthy_beats_regressed() -> None:
    healthy = _full_inputs()
    healthy.lifecycle_state = "healthy"

    regressed = _full_inputs()
    regressed.lifecycle_state = "regressed"

    assert compute_scores(healthy).lifecycle_score > compute_scores(regressed).lifecycle_score


def test_scoring_provenance_origin_type_affects_score() -> None:
    blueprint = _full_inputs()
    blueprint.origin_type = "blueprint-generated"

    adopted = _full_inputs()
    adopted.origin_type = "community-adopted"

    unknown = _full_inputs()
    unknown.origin_type = "unknown"

    assert compute_scores(blueprint).provenance_score >= compute_scores(adopted).provenance_score
    assert compute_scores(adopted).provenance_score > compute_scores(unknown).provenance_score


def test_scoring_reuse_count_increases_reuse_score() -> None:
    no_reuse = _full_inputs()
    no_reuse.reuse_count = 0

    some_reuse = _full_inputs()
    some_reuse.reuse_count = 3

    assert compute_scores(no_reuse).reuse_score == 0.0
    assert compute_scores(some_reuse).reuse_score > 0.0


def test_scoring_dimensions_match_count() -> None:
    snapshot = compute_scores(_full_inputs())

    assert len(snapshot.dimensions) == 6
    dim_names = {d.name for d in snapshot.dimensions}
    assert dim_names == {"structure", "quality", "eval", "lifecycle", "provenance", "reuse"}


def test_scoring_evidence_strings_are_informative() -> None:
    snapshot = compute_scores(_full_inputs())

    for dim in snapshot.dimensions:
        assert dim.evidence is not None
        assert len(dim.evidence) > 0


def test_suggested_state_promoted_when_high_promotion_score() -> None:
    assert suggested_state(0.9, 0.8) == "promoted"


def test_suggested_state_curated_when_moderate_collection_score() -> None:
    assert suggested_state(0.6, 0.5) == "curated"


def test_suggested_state_candidate_when_low_scores() -> None:
    assert suggested_state(0.3, 0.2) == "candidate"


def test_suggested_state_boundaries() -> None:
    assert suggested_state(PROMOTION_THRESHOLD, PROMOTION_THRESHOLD) == "promoted"
    assert suggested_state(CURATED_THRESHOLD, CURATED_THRESHOLD - 0.01) == "curated"
    assert suggested_state(CURATED_THRESHOLD - 0.01, 0.0) == "candidate"


def test_scoring_snapshot_roundtrips_through_store(tmp_path: Path) -> None:
    store = CollectionStore(tmp_path / "collections")
    snapshot = compute_scores(_full_inputs())
    snapshot.skill_id = "test-skill"

    store.write_snapshot(snapshot)
    loaded = store.read_snapshot("test-skill")

    assert loaded is not None
    assert loaded.final_collection_score == snapshot.final_collection_score
    assert loaded.final_promotion_score == snapshot.final_promotion_score
    assert len(loaded.dimensions) == 6


def test_custom_weights_change_scores() -> None:
    inputs = _full_inputs()
    default_snap = compute_scores(inputs)

    custom_config = ScoringConfig(
        collection_weights={
            "structure": 0.50,
            "quality": 0.10,
            "eval": 0.10,
            "lifecycle": 0.10,
            "provenance": 0.10,
            "reuse": 0.10,
        },
    )
    custom_snap = compute_scores(inputs, config=custom_config)

    assert custom_snap.final_collection_score != default_snap.final_collection_score


def test_custom_thresholds_affect_suggested_state() -> None:
    assert suggested_state(0.60, 0.60) == "curated"

    low_threshold = ScoringConfig(promotion_threshold=0.50, curated_threshold=0.30)
    assert suggested_state(0.60, 0.60, config=low_threshold) == "promoted"
