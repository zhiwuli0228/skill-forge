from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.models.collection import CollectionState, build_collection_record
from skill_forge.models.eval import SkillEvalReport
from skill_forge.models.generated import GenerationProvenanceMetadata
from skill_forge.models.quality import ContentQualityMetrics
from skill_forge.storage.collection_store import CollectionStore


runner = CliRunner()


def _write_skill(
    output_dir: Path,
    name: str,
    *,
    provenance: GenerationProvenanceMetadata | None = None,
    report: SkillEvalReport | None = None,
) -> Path:
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Sample skill.\n---\n\n# {name}\n\nBody.\n",
        encoding="utf-8",
    )
    if provenance is not None:
        (skill_dir / "skill-forge.json").write_text(provenance.model_dump_json(indent=2), encoding="utf-8")
    if report is not None:
        (skill_dir / "eval-report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return skill_dir


def _build_provenance(name: str, *, quality_score: int = 90) -> GenerationProvenanceMetadata:
    return GenerationProvenanceMetadata(
        generated_at="2026-06-07T00:00:00Z",
        skill_name=name,
        requirement_text="Sample",
        target_platform="codex",
        language="en",
        task_type="code-review",
        quality_score=quality_score,
        quality_status="valid",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.85,
            constraint_verifiability=0.80,
            quality_gate_clarity=0.82,
        ),
    )


def test_collection_list_empty(tmp_path: Path) -> None:
    home = tmp_path / "home"
    result = runner.invoke(app, ["collection", "list", "--home", str(home)])

    assert result.exit_code == 0
    assert "No collection records found" in result.output


def test_collection_list_shows_records(tmp_path: Path) -> None:
    home = tmp_path / "home"
    store = CollectionStore(home / "collections")
    store.write_record(build_collection_record(skill_id="alpha", package_name="alpha", origin_type="generated"))
    store.write_record(build_collection_record(skill_id="beta", package_name="beta", origin_type="adopted", collection_state=CollectionState.PROMOTED))

    result = runner.invoke(app, ["collection", "list", "--home", str(home)])

    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output
    assert "promoted" in result.output


def test_collection_list_filter_by_state(tmp_path: Path) -> None:
    home = tmp_path / "home"
    store = CollectionStore(home / "collections")
    store.write_record(build_collection_record(skill_id="alpha", package_name="alpha", origin_type="generated"))
    store.write_record(build_collection_record(skill_id="beta", package_name="beta", origin_type="generated", collection_state=CollectionState.PROMOTED))

    result = runner.invoke(app, ["collection", "list", "--state", "promoted", "--home", str(home)])

    assert result.exit_code == 0
    assert "beta" in result.output
    assert "alpha" not in result.output


def test_collection_list_invalid_state(tmp_path: Path) -> None:
    home = tmp_path / "home"
    result = runner.invoke(app, ["collection", "list", "--state", "invalid", "--home", str(home)])

    assert result.exit_code == 1
    assert "Invalid collection state" in result.output


def test_collection_show_displays_record(tmp_path: Path) -> None:
    home = tmp_path / "home"
    store = CollectionStore(home / "collections")
    record = build_collection_record(skill_id="test-skill", package_name="test-skill", origin_type="generated", rationale="Test")
    store.write_record(record)

    result = runner.invoke(app, ["collection", "show", "test-skill", "--home", str(home)])

    assert result.exit_code == 0
    assert "test-skill" in result.output
    assert "candidate" in result.output
    assert "Test" in result.output


def test_collection_show_missing(tmp_path: Path) -> None:
    home = tmp_path / "home"
    result = runner.invoke(app, ["collection", "show", "missing", "--home", str(home)])

    assert result.exit_code == 1
    assert "not found" in result.output


def test_collection_update_changes_state(tmp_path: Path) -> None:
    home = tmp_path / "home"
    store = CollectionStore(home / "collections")
    store.write_record(build_collection_record(skill_id="test-skill", package_name="test-skill", origin_type="generated"))

    result = runner.invoke(app, ["collection", "update", "test-skill", "--state", "curated", "--rationale", "High quality", "--home", str(home)])

    assert result.exit_code == 0
    assert "curated" in result.output

    record = store.read_record("test-skill")
    assert record is not None
    assert record.collection_state == CollectionState.CURATED
    assert record.rationale == "High quality"


def test_collection_update_invalid_state(tmp_path: Path) -> None:
    home = tmp_path / "home"
    store = CollectionStore(home / "collections")
    store.write_record(build_collection_record(skill_id="test-skill", package_name="test-skill", origin_type="generated"))

    result = runner.invoke(app, ["collection", "update", "test-skill", "--state", "bogus", "--home", str(home)])

    assert result.exit_code == 1
    assert "Invalid collection state" in result.output


def test_collection_update_missing_record(tmp_path: Path) -> None:
    home = tmp_path / "home"
    result = runner.invoke(app, ["collection", "update", "missing", "--state", "curated", "--home", str(home)])

    assert result.exit_code == 1
    assert "not found" in result.output


def test_collection_score_creates_record_and_snapshot(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    provenance = _build_provenance("sample")
    _write_skill(output_dir, "sample", provenance=provenance)

    result = runner.invoke(app, ["collection", "score", "sample", "--home", str(home)])

    assert result.exit_code == 0
    assert "Collection score" in result.output
    assert "structure" in result.output
    assert "quality" in result.output

    store = CollectionStore(home / "collections")
    record = store.read_record("sample")
    assert record is not None
    assert record.collection_score > 0
    assert record.promotion_score > 0

    snapshot = store.read_snapshot("sample")
    assert snapshot is not None
    assert len(snapshot.dimensions) == 6


def test_collection_score_updates_existing_record(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    store = CollectionStore(home / "collections")
    store.write_record(build_collection_record(skill_id="sample", package_name="sample", origin_type="generated"))
    provenance = _build_provenance("sample")
    _write_skill(output_dir, "sample", provenance=provenance)

    result = runner.invoke(app, ["collection", "score", "sample", "--home", str(home)])

    assert result.exit_code == 0
    record = store.read_record("sample")
    assert record is not None
    assert record.collection_score > 0


def test_list_shows_collection_state(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    store = CollectionStore(home / "collections")
    _write_skill(output_dir, "alpha")
    store.write_record(build_collection_record(skill_id="alpha", package_name="alpha", origin_type="generated", collection_state=CollectionState.PROMOTED))

    result = runner.invoke(app, ["list", "--home", str(home)])

    assert result.exit_code == 0
    assert "promoted" in result.output


def test_show_displays_collection_metadata(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    store = CollectionStore(home / "collections")
    _write_skill(output_dir, "sample")
    record = build_collection_record(skill_id="sample", package_name="sample", origin_type="generated", collection_state=CollectionState.CURATED, rationale="Good")
    record.collection_score = 0.75
    record.promotion_score = 0.60
    store.write_record(record)

    result = runner.invoke(app, ["show", "sample", "--home", str(home)])

    assert result.exit_code == 0
    assert "curated" in result.output
    assert "0.75" in result.output
    assert "Good" in result.output


def test_show_indicates_not_tracked_when_no_collection(tmp_path: Path) -> None:
    home = tmp_path / "home"
    output_dir = home / "output"
    _write_skill(output_dir, "sample")

    result = runner.invoke(app, ["show", "sample", "--home", str(home)])

    assert result.exit_code == 0
    assert "not tracked" in result.output
