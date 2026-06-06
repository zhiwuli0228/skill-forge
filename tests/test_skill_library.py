from pathlib import Path
import json

import pytest

from skill_forge.library.manager import (
    GeneratedSkillMissingSkillMdError,
    GeneratedSkillNotFoundError,
    SkillLibraryManager,
)
from skill_forge.models.eval import SkillEvalReport
from skill_forge.models.generated import GenerationProvenanceMetadata


def _write_skill(output_dir: Path, name: str, *, description: str = "Description.", body: str = "Body") -> Path:
    skill_dir = output_dir / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n\n{body}\n",
        encoding="utf-8",
    )
    return skill_dir


def test_library_lists_generated_skills(tmp_path: Path) -> None:
    _write_skill(tmp_path, "beta")
    _write_skill(tmp_path, "alpha")
    (tmp_path / "not-a-skill").mkdir()

    entries = SkillLibraryManager(tmp_path).list()

    assert [entry.name for entry in entries] == ["alpha", "beta"]


def test_library_show_reads_metadata_and_attachment_counts(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "sample", description="Sample skill.")
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "one.md").write_text("one", encoding="utf-8")
    (skill_dir / "assets").mkdir()
    (skill_dir / "assets" / "image.txt").write_text("asset", encoding="utf-8")

    entry = SkillLibraryManager(tmp_path).show("sample")

    assert entry.name == "sample"
    assert entry.frontmatter_name == "sample"
    assert entry.description == "Sample skill."
    assert entry.reference_count == 1
    assert entry.asset_count == 1
    assert entry.script_count == 0
    assert entry.provenance is None


def test_library_show_reads_generation_provenance(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "sample", description="Sample skill.")
    metadata = GenerationProvenanceMetadata(
        generated_at="2026-05-26T00:00:00Z",
        skill_name="sample",
        requirement_text="sample skill",
        target_platform="opencode",
        language="zh-CN",
        task_type="code-review",
        blueprint_id="team-code-review",
        blueprint_source="project",
        llm_enabled=False,
        project_context_path=None,
        quality_score=95,
        quality_status="valid_with_warnings",
    )
    (skill_dir / "skill-forge.json").write_text(metadata.model_dump_json(indent=2), encoding="utf-8")

    entry = SkillLibraryManager(tmp_path).show("sample")

    assert entry.provenance is not None
    assert entry.provenance.blueprint_id == "team-code-review"
    assert entry.provenance.quality_score == 95


def test_library_show_reads_adoption_provenance(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "sample", description="Sample skill.")
    metadata = GenerationProvenanceMetadata(
        origin_type="community-adopted",
        generated_at="2026-05-28T00:00:00Z",
        adopted_at="2026-05-28T00:00:00Z",
        skill_name="sample",
        requirement_text="",
        target_platform="codex",
        language="unknown",
        quality_score=90,
        quality_status="valid_with_warnings",
        source_name="Community Repo",
        source_url="https://github.com/example/skills",
        document_url="https://raw.githubusercontent.com/example/skills/main/sample/SKILL.md",
        document_id=7,
        example_id=8,
        source_platform="codex",
        content_hash="hash-1",
    )
    (skill_dir / "skill-forge.json").write_text(metadata.model_dump_json(indent=2), encoding="utf-8")

    entry = SkillLibraryManager(tmp_path).show("sample")

    assert entry.provenance is not None
    assert entry.provenance.origin_type == "community-adopted"
    assert entry.provenance.source_name == "Community Repo"
    assert entry.provenance.document_id == 7


def test_library_show_reads_eval_report(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path, "sample", description="Sample skill.")
    report = SkillEvalReport(skill_name="sample", total=2, passed=1, failed=1)
    (skill_dir / "eval-report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")

    entry = SkillLibraryManager(tmp_path).show("sample")

    assert entry.eval_report is not None
    assert entry.eval_report.total == 2
    assert entry.eval_report.passed == 1
    assert entry.eval_report.failed == 1


def test_library_show_reports_missing_skill(tmp_path: Path) -> None:
    with pytest.raises(GeneratedSkillNotFoundError):
        SkillLibraryManager(tmp_path).show("missing")


def test_library_show_reports_missing_skill_md(tmp_path: Path) -> None:
    (tmp_path / "broken").mkdir()

    with pytest.raises(GeneratedSkillMissingSkillMdError):
        SkillLibraryManager(tmp_path).show("broken")


def test_library_diff_returns_unified_diff(tmp_path: Path) -> None:
    _write_skill(tmp_path, "left", body="Left")
    _write_skill(tmp_path, "right", body="Right")

    diff = SkillLibraryManager(tmp_path).diff("left", "right")

    assert diff[0].startswith("--- left/SKILL.md")
    assert diff[1].startswith("+++ right/SKILL.md")
    assert any("-Left" in line for line in diff)
    assert any("+Right" in line for line in diff)


def test_library_diff_returns_empty_list_for_identical_skill_md(tmp_path: Path) -> None:
    left = _write_skill(tmp_path, "left", body="Same")
    right = _write_skill(tmp_path, "right", body="Same")
    right.joinpath("SKILL.md").write_text(left.joinpath("SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")

    assert SkillLibraryManager(tmp_path).diff("left", "right") == []


def test_library_diff_includes_metadata_differences(tmp_path: Path) -> None:
    left = _write_skill(tmp_path, "left", body="Same")
    right = _write_skill(tmp_path, "right", body="Same")
    right.joinpath("SKILL.md").write_text(left.joinpath("SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")
    left.joinpath("skill-forge.json").write_text(json.dumps({"schema_version": 1, "skill_name": "left"}), encoding="utf-8")

    diff = SkillLibraryManager(tmp_path).diff("left", "right")

    assert diff[0].startswith("--- left/skill-forge.json")
    assert diff[1].startswith("+++ right/skill-forge.json")
    assert any('"skill_name": "left"' in line for line in diff)
