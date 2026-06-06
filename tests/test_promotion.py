import json
from pathlib import Path

from typer.testing import CliRunner

from skill_forge.cli import app
from skill_forge.lifecycle.promotion import PromotionSnapshotNotFoundError, SkillPromotionService
from skill_forge.library.manager import SkillLibraryManager


runner = CliRunner()


def _create_source_and_candidate(home: Path) -> tuple[Path, Path]:
    create_result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    upgrade_result = runner.invoke(app, ["upgrade", "java-bug-investigation", "--home", str(home)])

    assert create_result.exit_code == 0
    assert upgrade_result.exit_code == 0
    source = home / "output" / "java-bug-investigation"
    candidate = home / "output" / "java-bug-investigation-upgraded"
    return source, candidate


def test_promotion_service_promotes_candidate_and_preserves_source(tmp_path: Path) -> None:
    home = tmp_path / "home"
    source, candidate = _create_source_and_candidate(home)
    source_before = source.joinpath("SKILL.md").read_text(encoding="utf-8")
    candidate_before = candidate.joinpath("SKILL.md").read_text(encoding="utf-8")

    result = SkillPromotionService(SkillLibraryManager(home / "output"), home / "promotions").promote(
        "java-bug-investigation-upgraded"
    )

    registry = json.loads(result.registry_path.read_text(encoding="utf-8"))
    promoted_target = home / "output" / "java-bug-investigation"

    assert result.candidate_name == "java-bug-investigation-upgraded"
    assert result.target_name == "java-bug-investigation"
    assert result.previous_version_name == "java-bug-investigation"
    assert promoted_target.joinpath("SKILL.md").read_text(encoding="utf-8") == candidate_before
    assert candidate.joinpath("SKILL.md").read_text(encoding="utf-8") == candidate_before
    assert source.joinpath("SKILL.md").read_text(encoding="utf-8") == candidate_before
    assert source_before != candidate_before
    assert registry["active_version_name"] == "java-bug-investigation-upgraded"
    assert registry["history"][0]["snapshot_version_name"] == "java-bug-investigation"
    assert registry["history"][0]["snapshot_path"]


def test_promotion_service_rollback_restores_snapshot(tmp_path: Path) -> None:
    home = tmp_path / "home"
    source, candidate = _create_source_and_candidate(home)
    original_source = source.joinpath("SKILL.md").read_text(encoding="utf-8")
    service = SkillPromotionService(SkillLibraryManager(home / "output"), home / "promotions")

    promote_result = service.promote("java-bug-investigation-upgraded")
    rollback_result = service.rollback("java-bug-investigation", version_name="java-bug-investigation")

    registry = json.loads(rollback_result.registry_path.read_text(encoding="utf-8"))

    assert promote_result.snapshot_path is not None
    assert rollback_result.previous_version_name == "java-bug-investigation-upgraded"
    assert source.joinpath("SKILL.md").read_text(encoding="utf-8") == original_source
    assert candidate.joinpath("SKILL.md").read_text(encoding="utf-8") != original_source
    assert registry["active_version_name"] == "java-bug-investigation"
    assert registry["history"][-1]["operation"] == "rollback"
    assert registry["history"][-1]["snapshot_version_name"] == "java-bug-investigation-upgraded"


def test_promotion_service_rollback_reports_missing_history(tmp_path: Path) -> None:
    home = tmp_path / "home"
    _create_source_and_candidate(home)
    service = SkillPromotionService(SkillLibraryManager(home / "output"), home / "promotions")

    try:
        service.rollback("java-bug-investigation", version_name="missing-version")
    except PromotionSnapshotNotFoundError as exc:
        assert exc.skill_name == "java-bug-investigation"
        assert exc.version_name == "missing-version"
    else:
        raise AssertionError("rollback should fail when the requested version snapshot does not exist")


def test_promote_and_rollback_cli_are_read_write_and_report_history(tmp_path: Path) -> None:
    home = tmp_path / "home"
    source, candidate = _create_source_and_candidate(home)
    candidate_before = candidate.joinpath("SKILL.md").read_text(encoding="utf-8")

    promote_result = runner.invoke(app, ["promote", "java-bug-investigation-upgraded", "--home", str(home)])
    rollback_result = runner.invoke(
        app,
        ["rollback", "java-bug-investigation", "--to", "java-bug-investigation", "--home", str(home)],
    )

    promoted_target = home / "output" / "java-bug-investigation"

    assert promote_result.exit_code == 0
    assert "Skill promoted" in promote_result.output
    assert "Registry" in promote_result.output
    assert rollback_result.exit_code == 0
    assert "Skill rolled back" in rollback_result.output
    assert promoted_target.joinpath("SKILL.md").read_text(encoding="utf-8") != candidate_before
    assert candidate.joinpath("SKILL.md").read_text(encoding="utf-8") == candidate_before


def test_promote_cli_fails_for_missing_candidate(tmp_path: Path) -> None:
    result = runner.invoke(app, ["promote", "missing", "--home", str(tmp_path / "home")])

    assert result.exit_code == 1
    assert "Generated Skill package not found" in result.output
