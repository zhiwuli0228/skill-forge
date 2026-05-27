import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from skill_forge.blueprints.enricher import BlueprintRequirementEnricher
from skill_forge.blueprints.loader import BlueprintLoader
from skill_forge.cli import app
from skill_forge.generator.skill_generator import SkillGenerator
from skill_forge.models.generated import GenerationProvenanceMetadata
from skill_forge.models.quality import build_generation_quality_report
from skill_forge.requirement.analyzer import RequirementAnalyzer
from skill_forge.upgrade.service import (
    CandidateExistsError,
    MissingUpgradeBlueprintError,
    MissingUpgradeProvenanceError,
    SkillUpgradeService,
)
from skill_forge.validator.skill_validator import SkillValidator


runner = CliRunner()


CUSTOM_BLUEPRINT = """
id: team-code-review
name: Team Code Review
description: Review code using the team's private standard.
task_type: team-code-review
workflow:
  - Apply the team-specific review checklist.
constraints:
  - Require team ownership notes.
expected_outputs:
  - Team Findings
quality_gates:
  - Findings must reference team standards.
"""


def _write_blueprint(directory: Path, name: str, body: str = CUSTOM_BLUEPRINT) -> Path:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _create_generated_source(output_dir: Path, requirement_text: str = "Java 存量代码 bug 定位 skill") -> Path:
    requirement = RequirementAnalyzer().analyze(requirement_text)
    requirement = BlueprintRequirementEnricher().enrich(requirement)
    package = SkillGenerator().generate(requirement, output_dir)
    quality = build_generation_quality_report(
        SkillValidator().validate(package.path, attachment_paths=[*package.references, *package.assets, *package.scripts])
    )
    metadata = GenerationProvenanceMetadata(
        generated_at="2026-05-27T00:00:00Z",
        skill_name=package.name,
        requirement_text=requirement_text,
        target_platform=package.target_platform,
        language=requirement.language,
        task_type=requirement.task_type,
        blueprint_id=requirement.applied_blueprint_id,
        blueprint_source=requirement.applied_blueprint_source,
        llm_enabled=False,
        project_context_path=None,
        quality_score=quality.score,
        quality_status=quality.status,
        references=sorted(package.references),
        assets=sorted(package.assets),
        scripts=sorted(package.scripts),
    )
    (package.path / "skill-forge.json").write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
    return package.path


def test_upgrade_service_generates_candidate_and_preserves_source(tmp_path: Path) -> None:
    source = _create_generated_source(tmp_path)
    original_content = source.joinpath("SKILL.md").read_text(encoding="utf-8")

    result = SkillUpgradeService(output_dir=tmp_path).upgrade(source)

    candidate = tmp_path / "java-bug-investigation-upgraded"
    metadata = json.loads(candidate.joinpath("skill-forge.json").read_text(encoding="utf-8"))
    assert result.candidate_name == "java-bug-investigation-upgraded"
    assert candidate.joinpath("SKILL.md").is_file()
    assert source.joinpath("SKILL.md").read_text(encoding="utf-8") == original_content
    assert metadata["skill_name"] == "java-bug-investigation-upgraded"
    assert metadata["blueprint_id"] == "bug-investigation"
    assert result.previous_quality_score == 100
    assert result.candidate_quality_report.ok is True


def test_upgrade_service_uses_custom_candidate_name(tmp_path: Path) -> None:
    source = _create_generated_source(tmp_path)

    result = SkillUpgradeService(output_dir=tmp_path).upgrade(source, candidate_name="java-bug-v2")

    assert result.candidate_name == "java-bug-v2"
    assert (tmp_path / "java-bug-v2" / "SKILL.md").is_file()


def test_upgrade_service_requires_provenance(tmp_path: Path) -> None:
    source = tmp_path / "legacy"
    source.mkdir()
    source.joinpath("SKILL.md").write_text("---\nname: legacy\ndescription: legacy\n---\n", encoding="utf-8")

    with pytest.raises(MissingUpgradeProvenanceError):
        SkillUpgradeService(output_dir=tmp_path).upgrade(source)


def test_upgrade_service_reports_missing_blueprint(tmp_path: Path) -> None:
    source = _create_generated_source(tmp_path)
    metadata = json.loads(source.joinpath("skill-forge.json").read_text(encoding="utf-8"))
    metadata["blueprint_id"] = "missing-blueprint"
    source.joinpath("skill-forge.json").write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(MissingUpgradeBlueprintError, match="missing-blueprint"):
        SkillUpgradeService(output_dir=tmp_path).upgrade(source)


def test_upgrade_service_rejects_existing_candidate_and_force_replaces_it(tmp_path: Path) -> None:
    source = _create_generated_source(tmp_path)
    candidate = tmp_path / "java-bug-investigation-upgraded"
    candidate.mkdir()
    candidate.joinpath("old.txt").write_text("old", encoding="utf-8")

    with pytest.raises(CandidateExistsError):
        SkillUpgradeService(output_dir=tmp_path).upgrade(source)

    result = SkillUpgradeService(output_dir=tmp_path).upgrade(source, force=True)

    assert result.candidate_name == "java-bug-investigation-upgraded"
    assert candidate.joinpath("SKILL.md").is_file()
    assert not candidate.joinpath("old.txt").exists()


def test_upgrade_cli_generates_candidate(tmp_path: Path) -> None:
    home = tmp_path / "home"
    create = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    result = runner.invoke(app, ["upgrade", "java-bug-investigation", "--home", str(home)])

    assert create.exit_code == 0
    assert result.exit_code == 0
    assert "Skill upgrade candidate" in result.output
    assert "java-bug-investigation-upgraded" in result.output
    assert "Previous quality" in result.output
    assert "Candidate quality" in result.output
    assert (home / "output" / "java-bug-investigation-upgraded" / "SKILL.md").is_file()


def test_upgrade_cli_accepts_custom_candidate_name(tmp_path: Path) -> None:
    home = tmp_path / "home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    result = runner.invoke(
        app,
        ["upgrade", "java-bug-investigation", "--candidate-name", "java-bug-v2", "--home", str(home)],
    )

    assert result.exit_code == 0
    assert (home / "output" / "java-bug-v2" / "SKILL.md").is_file()


def test_upgrade_cli_fails_without_provenance(tmp_path: Path) -> None:
    home = tmp_path / "home"
    legacy = home / "output" / "legacy"
    legacy.mkdir(parents=True)
    legacy.joinpath("SKILL.md").write_text(
        "---\nname: legacy\ndescription: Use this skill for legacy work. Do not use it elsewhere.\n---\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["upgrade", "legacy", "--home", str(home)])

    assert result.exit_code == 1
    assert "Upgrade requires provenance metadata" in result.output


def test_upgrade_cli_fails_when_blueprint_is_missing(tmp_path: Path) -> None:
    home = tmp_path / "home"
    blueprint_path = _write_blueprint(home / "blueprints", "team-code-review.yaml")
    create = runner.invoke(
        app,
        ["create", "团队代码审查 skill", "--blueprint", "team-code-review", "--home", str(home)],
    )
    blueprint_path.unlink()

    result = runner.invoke(app, ["upgrade", "code-review", "--home", str(home)])

    assert create.exit_code == 0
    assert result.exit_code == 1
    assert "Upgrade blueprint not found" in result.output
    assert "team-code-review" in result.output


def test_upgrade_cli_fails_for_existing_candidate_unless_forced(tmp_path: Path) -> None:
    home = tmp_path / "home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    first = runner.invoke(app, ["upgrade", "java-bug-investigation", "--home", str(home)])
    candidate = home / "output" / "java-bug-investigation-upgraded"
    candidate.joinpath("old.txt").write_text("old", encoding="utf-8")

    second = runner.invoke(app, ["upgrade", "java-bug-investigation", "--home", str(home)])
    forced = runner.invoke(app, ["upgrade", "java-bug-investigation", "--force", "--home", str(home)])

    assert first.exit_code == 0
    assert second.exit_code == 1
    assert "Upgrade candidate already exists" in second.output
    assert forced.exit_code == 0
    assert not candidate.joinpath("old.txt").exists()
    assert candidate.joinpath("SKILL.md").is_file()


def test_upgrade_candidate_can_be_listed_shown_and_diffed(tmp_path: Path) -> None:
    home = tmp_path / "home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    upgrade = runner.invoke(app, ["upgrade", "java-bug-investigation", "--home", str(home)])

    listed = runner.invoke(app, ["list", "--home", str(home)])
    shown = runner.invoke(app, ["show", "java-bug-investigation-upgraded", "--home", str(home)])
    diffed = runner.invoke(
        app,
        ["diff", "java-bug-investigation", "java-bug-investigation-upgraded", "--home", str(home)],
    )

    assert upgrade.exit_code == 0
    assert "java-bug-investigation-upgraded" in listed.output
    assert shown.exit_code == 0
    assert "Blueprint" in shown.output
    assert diffed.exit_code == 0
