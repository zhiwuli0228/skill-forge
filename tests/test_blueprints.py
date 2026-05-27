from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from skill_forge.blueprints.loader import (
    BlueprintLoadError,
    BlueprintLoader,
    BlueprintNotFoundError,
    DuplicateBlueprintError,
)
from skill_forge.blueprints.enricher import BlueprintRequirementEnricher, merge_blueprint_defaults, merge_list_values
from skill_forge.cli import app
from skill_forge.models.blueprint import BlueprintGeneratedFile, SkillBlueprint
from skill_forge.models.requirement import SkillRequirement


runner = CliRunner()


def write_blueprint(directory: Path, name: str, body: str) -> Path:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


VALID_BLUEPRINT = """
id: bug-investigation
name: Bug Investigation
description: Diagnose bugs from evidence.
task_type: bug-investigation
workflow:
  - Collect evidence.
expected_outputs:
  - Root Cause
"""


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


def test_skill_blueprint_validates_kebab_case_id() -> None:
    with pytest.raises(ValidationError, match="lowercase kebab-case"):
        SkillBlueprint(
            id="Bug Investigation",
            name="Bug Investigation",
            description="Diagnose bugs.",
            task_type="bug-investigation",
        )


def test_skill_blueprint_trims_list_items() -> None:
    blueprint = SkillBlueprint(
        id="bug-investigation",
        name="Bug Investigation",
        description="Diagnose bugs.",
        task_type="bug-investigation",
        workflow=[" Collect evidence. ", ""],
    )

    assert blueprint.workflow == ["Collect evidence."]


def test_generated_file_rejects_unsafe_paths() -> None:
    with pytest.raises(ValidationError, match="safe relative path"):
        BlueprintGeneratedFile(path="../escape.md", content="bad")

    with pytest.raises(ValidationError, match="safe relative path"):
        BlueprintGeneratedFile(path="/absolute.md", content="bad")


def test_loader_loads_built_in_blueprints_in_deterministic_order() -> None:
    blueprints = BlueprintLoader().load_all()

    assert [blueprint.id for blueprint in blueprints] == sorted(blueprint.id for blueprint in blueprints)
    assert {blueprint.id for blueprint in blueprints} == {
        "bug-investigation",
        "code-review",
        "openspec-change",
        "test-generation",
    }


def test_loader_loads_user_custom_blueprints_with_source_metadata(tmp_path: Path) -> None:
    user_dir = tmp_path / "home" / "blueprints"
    blueprint_path = write_blueprint(user_dir, "team-code-review.yaml", CUSTOM_BLUEPRINT)

    records = BlueprintLoader(user_blueprint_dir=user_dir).load_records()
    record = next(record for record in records if record.blueprint.id == "team-code-review")

    assert record.source == "user"
    assert record.path == blueprint_path
    assert record.blueprint.workflow == ["Apply the team-specific review checklist."]


def test_loader_loads_project_custom_blueprints_with_source_metadata(tmp_path: Path) -> None:
    project_dir = tmp_path / "project" / ".skill-forge" / "blueprints"
    blueprint_path = write_blueprint(project_dir, "team-code-review.yaml", CUSTOM_BLUEPRINT)

    records = BlueprintLoader(project_blueprint_dir=project_dir).load_records()
    record = next(record for record in records if record.blueprint.id == "team-code-review")

    assert record.source == "project"
    assert record.path == blueprint_path


def test_loader_ignores_missing_custom_blueprint_roots(tmp_path: Path) -> None:
    blueprints = BlueprintLoader(user_blueprint_dir=tmp_path / "missing-user").load_all()

    assert "bug-investigation" in {blueprint.id for blueprint in blueprints}


def test_loader_rejects_duplicate_blueprint_ids_across_roots(tmp_path: Path) -> None:
    user_dir = tmp_path / "home" / "blueprints"
    write_blueprint(user_dir, "bug.yaml", VALID_BLUEPRINT)

    with pytest.raises(DuplicateBlueprintError, match="bug-investigation") as error:
        BlueprintLoader(user_blueprint_dir=user_dir).load_all()

    assert len(error.value.paths) == 2


def test_loader_exposes_blueprint_declared_reference() -> None:
    blueprint = BlueprintLoader().get("bug-investigation")

    assert [file.path for file in blueprint.references] == ["references/diagnosis-checklist.md"]
    assert "Diagnosis Checklist" in blueprint.references[0].content


def test_loader_rejects_duplicate_blueprint_ids(tmp_path: Path) -> None:
    write_blueprint(tmp_path, "a.yaml", VALID_BLUEPRINT)
    write_blueprint(tmp_path, "b.yaml", VALID_BLUEPRINT)

    with pytest.raises(DuplicateBlueprintError, match="bug-investigation"):
        BlueprintLoader(tmp_path).load_all()


def test_loader_rejects_invalid_blueprint_file(tmp_path: Path) -> None:
    write_blueprint(
        tmp_path,
        "invalid.yaml",
        """
id: Invalid ID
name: Invalid
description: Invalid blueprint.
task_type: bug-investigation
""",
    )

    with pytest.raises(BlueprintLoadError, match="id"):
        BlueprintLoader(tmp_path).load_all()


def test_loader_rejects_unsafe_declared_file_path(tmp_path: Path) -> None:
    write_blueprint(
        tmp_path,
        "invalid-reference.yaml",
        """
id: invalid-reference
name: Invalid Reference
description: Invalid reference path.
task_type: invalid-reference
references:
  - path: ../escape.md
    content: bad
""",
    )

    with pytest.raises(BlueprintLoadError, match="references"):
        BlueprintLoader(tmp_path).load_all()


def test_loader_get_raises_for_missing_blueprint(tmp_path: Path) -> None:
    write_blueprint(tmp_path, "bug.yaml", VALID_BLUEPRINT)

    with pytest.raises(BlueprintNotFoundError, match="missing"):
        BlueprintLoader(tmp_path).get("missing")


def test_loader_finds_blueprint_by_task_type() -> None:
    blueprint = BlueprintLoader().find_by_task_type("bug-investigation")

    assert blueprint is not None
    assert blueprint.id == "bug-investigation"


def test_loader_returns_none_for_unknown_task_type() -> None:
    assert BlueprintLoader().find_by_task_type("unknown-task") is None
    assert BlueprintLoader().find_by_task_type(None) is None


def test_merge_list_values_deduplicates_case_insensitively() -> None:
    merged = merge_list_values(["Root Cause"], ["root cause", "Fix Plan"])

    assert merged == ["Root Cause", "Fix Plan"]


def test_merge_blueprint_defaults_preserves_requirement_values_first() -> None:
    requirement = SkillRequirement(
        name="custom-bug",
        description="Custom bug skill",
        task_type="bug-investigation",
        workflow=["User workflow"],
        expected_outputs=["Root Cause"],
    )
    blueprint = SkillBlueprint(
        id="bug-investigation",
        name="Bug Investigation",
        description="Diagnose bugs.",
        task_type="bug-investigation",
        workflow=["Blueprint workflow"],
        expected_outputs=["Root Cause", "Fix Plan"],
    )

    enriched = merge_blueprint_defaults(requirement, blueprint)

    assert enriched.name == "custom-bug"
    assert enriched.description == "Custom bug skill"
    assert enriched.workflow == ["User workflow", "Blueprint workflow"]
    assert enriched.expected_outputs == ["Root Cause", "Fix Plan"]


def test_blueprint_enricher_returns_requirement_when_no_blueprint_matches() -> None:
    requirement = SkillRequirement(
        name="generic-skill",
        description="Generic skill",
        task_type="unknown-task",
        workflow=["Generic workflow"],
    )

    enriched = BlueprintRequirementEnricher().enrich(requirement)

    assert enriched == requirement


def test_blueprint_enricher_can_use_explicit_blueprint_id() -> None:
    requirement = SkillRequirement(
        name="custom-review",
        description="Custom review skill",
        task_type=None,
        workflow=["User workflow"],
    )

    enriched = BlueprintRequirementEnricher().enrich(requirement, blueprint_id="code-review")

    assert enriched.name == "custom-review"
    assert "Prioritize findings by severity with file and line references when available." in enriched.workflow
    assert "Findings" in enriched.expected_outputs


def test_explicit_blueprint_id_overrides_task_type_matching() -> None:
    requirement = SkillRequirement(
        name="review-tests",
        description="Review tests",
        task_type="code-review",
    )

    enriched = BlueprintRequirementEnricher().enrich(requirement, blueprint_id="test-generation")

    assert "Test Matrix" in enriched.expected_outputs
    assert "Findings" not in enriched.expected_outputs


def test_blueprints_list_command_displays_built_ins() -> None:
    result = runner.invoke(app, ["blueprints", "list"])

    assert result.exit_code == 0
    assert "Skill blueprints" in result.output
    assert "Source" in result.output
    assert "builtin" in result.output
    assert "bug-investigation" in result.output
    assert "Bug Investigation" in result.output
    assert "code-review" in result.output
    assert "openspec-change" in result.output
    assert "test-generation" in result.output


def test_blueprints_show_command_displays_details() -> None:
    result = runner.invoke(app, ["blueprints", "show", "bug-investigation"])

    assert result.exit_code == 0
    assert "Blueprint: bug-investigation" in result.output
    assert "builtin" in result.output
    assert "Path" in result.output
    assert "Root Cause" in result.output
    assert "Collect symptoms and evidence" in result.output


def test_blueprints_list_command_displays_user_custom_blueprints(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_blueprint(home / "blueprints", "team-code-review.yaml", CUSTOM_BLUEPRINT)

    result = runner.invoke(app, ["blueprints", "list", "--home", str(home)])

    assert result.exit_code == 0
    assert "team-code-review" in result.output
    assert "user" in result.output


def test_blueprints_show_command_displays_project_custom_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    write_blueprint(project / ".skill-forge" / "blueprints", "team-code-review.yaml", CUSTOM_BLUEPRINT)

    result = runner.invoke(
        app,
        ["blueprints", "show", "team-code-review", "--home", str(home), "--project", str(project)],
    )

    assert result.exit_code == 0
    assert "Blueprint: team-code-review" in result.output
    assert "project" in result.output
    assert "Apply the team-specific review checklist" in result.output


def test_blueprints_list_command_fails_for_duplicate_custom_blueprints(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_blueprint(home / "blueprints", "bug.yaml", VALID_BLUEPRINT)

    result = runner.invoke(app, ["blueprints", "list", "--home", str(home)])

    assert result.exit_code == 1
    assert "Duplicate blueprint id" in result.output
    assert "bug-investigation" in result.output


def test_blueprints_show_command_displays_expanded_blueprint_details() -> None:
    result = runner.invoke(app, ["blueprints", "show", "code-review"])

    assert result.exit_code == 0
    assert "Blueprint: code-review" in result.output
    assert "Findings" in result.output
    assert "Prioritize findings by severity" in result.output


def test_blueprints_show_command_fails_for_missing_blueprint() -> None:
    result = runner.invoke(app, ["blueprints", "show", "missing-blueprint"])

    assert result.exit_code == 1
    assert "Blueprint not found" in result.output
    assert "missing-blueprint" in result.output


def test_existing_create_behavior_remains_available(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    assert result.exit_code == 0
    assert (home / "output" / "java-bug-investigation" / "SKILL.md").is_file()


def test_create_uses_matching_blueprint_defaults(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    content = (home / "output" / "java-bug-investigation" / "SKILL.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Do not modify code before identifying an evidence-backed root cause." in content
    assert "Build an evidence-backed root-cause chain." in content


def test_create_writes_blueprint_declared_reference(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    reference = home / "output" / "java-bug-investigation" / "references" / "diagnosis-checklist.md"
    assert result.exit_code == 0
    assert reference.is_file()
    assert "Diagnosis Checklist" in reference.read_text(encoding="utf-8")


def test_create_falls_back_without_matching_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--home", str(home)])

    generated = list((home / "output").glob("*/SKILL.md"))
    assert result.exit_code == 0
    assert len(generated) == 1
    content = generated[0].read_text(encoding="utf-8")
    assert "确认用户目标和边界" in content
    assert "evidence-backed root cause" not in content


def test_create_with_project_keeps_project_constraints_after_blueprint_defaults(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("Use OpenSpec proposal and change workflow.", encoding="utf-8")

    result = runner.invoke(
        app,
        ["create", "Java 存量代码 bug 定位 skill", "--project", str(project), "--home", str(home)],
    )

    content = (home / "output" / "java-bug-investigation" / "SKILL.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Do not modify code before identifying an evidence-backed root cause." in content
    assert "Project constraint: Use the OpenSpec change workflow" in content


def test_create_uses_code_review_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(app, ["create", "Python 代码审查 skill", "--home", str(home)])

    content = (home / "output" / "code-review" / "SKILL.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Prioritize findings by severity" in content
    assert "Test Gaps" in content
    assert not (home / "output" / "code-review" / "references").exists()


def test_create_uses_test_generation_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(app, ["create", "为这个项目生成测试编写 skill", "--home", str(home)])

    content = (home / "output" / "test-generation" / "SKILL.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Build a focused test matrix" in content
    assert "Verification Command" in content


def test_create_uses_openspec_change_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(app, ["create", "OpenSpec change 分析 skill", "--home", str(home)])

    content = (home / "output" / "openspec-change" / "SKILL.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Create or update proposal, design, specs, and tasks" in content
    assert "Archive Status" in content


def test_create_can_use_explicit_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(
        app,
        ["create", "Python 服务 review", "--blueprint", "code-review", "--home", str(home)],
    )

    generated = list((home / "output").glob("*/SKILL.md"))
    assert result.exit_code == 0
    assert len(generated) == 1
    content = generated[0].read_text(encoding="utf-8")
    assert "Prioritize findings by severity" in content
    assert "Test Gaps" in content


def test_create_can_use_user_custom_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_blueprint(home / "blueprints", "team-code-review.yaml", CUSTOM_BLUEPRINT)

    result = runner.invoke(
        app,
        ["create", "团队代码审查 skill", "--blueprint", "team-code-review", "--home", str(home)],
    )

    generated = list((home / "output").glob("*/SKILL.md"))
    assert result.exit_code == 0
    assert len(generated) == 1
    content = generated[0].read_text(encoding="utf-8")
    assert "Apply the team-specific review checklist" in content
    assert "Team Findings" in content


def test_create_can_use_project_custom_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    write_blueprint(project / ".skill-forge" / "blueprints", "team-code-review.yaml", CUSTOM_BLUEPRINT)

    result = runner.invoke(
        app,
        [
            "create",
            "团队代码审查 skill",
            "--blueprint",
            "team-code-review",
            "--project",
            str(project),
            "--home",
            str(home),
        ],
    )

    generated = list((home / "output").glob("*/SKILL.md"))
    assert result.exit_code == 0
    assert len(generated) == 1
    content = generated[0].read_text(encoding="utf-8")
    assert "Apply the team-specific review checklist" in content
    assert "Require team ownership notes" in content


def test_create_fails_for_duplicate_blueprint_ids_across_roots(tmp_path: Path) -> None:
    home = tmp_path / "home"
    write_blueprint(home / "blueprints", "bug.yaml", VALID_BLUEPRINT)

    result = runner.invoke(
        app,
        ["create", "Java 存量代码 bug 定位 skill", "--blueprint", "bug-investigation", "--home", str(home)],
    )

    assert result.exit_code == 1
    assert "Duplicate blueprint id" in result.output
    assert "bug-investigation" in result.output


def test_create_explicit_blueprint_overrides_automatic_match(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(
        app,
        ["create", "Python 代码审查 skill", "--blueprint", "test-generation", "--home", str(home)],
    )

    content = (home / "output" / "code-review" / "SKILL.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Build a focused test matrix" in content
    assert "Prioritize findings by severity" not in content


def test_create_fails_for_missing_explicit_blueprint(tmp_path: Path) -> None:
    home = tmp_path / "home"

    result = runner.invoke(
        app,
        ["create", "Python 服务 review", "--blueprint", "missing-blueprint", "--home", str(home)],
    )

    assert result.exit_code == 1
    assert "Blueprint not found" in result.output
    assert "missing-blueprint" in result.output
    assert not list((home / "output").glob("*/SKILL.md"))


def test_interactive_create_uses_explicit_blueprint(tmp_path: Path, monkeypatch) -> None:
    from skill_forge.interaction.wizard import QuestionaryPromptAdapter

    home = tmp_path / "home"
    monkeypatch.setattr(QuestionaryPromptAdapter, "text", lambda self, message, default="": default)
    monkeypatch.setattr(QuestionaryPromptAdapter, "multiline", lambda self, message, default: default)

    result = runner.invoke(
        app,
        ["create", "Python 服务 review", "--blueprint", "code-review", "--interactive", "--home", str(home)],
    )

    generated = list((home / "output").glob("*/SKILL.md"))
    assert result.exit_code == 0
    assert generated
    assert "Prioritize findings by severity" in generated[0].read_text(encoding="utf-8")


def test_create_with_project_uses_explicit_blueprint_and_project_constraints(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("Use OpenSpec proposal and change workflow.", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "create",
            "Python 服务 review",
            "--blueprint",
            "code-review",
            "--project",
            str(project),
            "--home",
            str(home),
        ],
    )

    generated = list((home / "output").glob("*/SKILL.md"))
    assert result.exit_code == 0
    content = generated[0].read_text(encoding="utf-8")
    assert "Prioritize findings by severity" in content
    assert "Project constraint: Use the OpenSpec change workflow" in content
