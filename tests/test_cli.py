import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import skill_forge.cli as cli_module
from skill_forge.cli import app
from skill_forge.models.experience import ExperienceRule
from skill_forge.models.eval import SkillEvalAssertionResult, SkillEvalCaseResult, SkillEvalReport
from skill_forge.models.generated import GenerationProvenanceMetadata
from skill_forge.models.quality import ContentQualityMetrics
from skill_forge.interaction.wizard import QuestionaryPromptAdapter
from skill_forge.models.validation import ValidationIssue, ValidationResult
from skill_forge.retrieval.generation import GenerationRetrievalContext
from skill_forge.storage.sqlite_store import list_tables
from skill_forge.validator.skill_validator import SkillValidator


runner = CliRunner()


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.seen_requirements = []

    def refine_requirement(self, requirement_text, requirement, retrieval_context=None) -> str:
        self.seen_requirements.append(requirement.model_copy(deep=True))
        return self.response

    def check_availability(self, *, timeout_seconds: float = 1.0) -> None:
        return None


@pytest.fixture(autouse=True)
def clear_llm_env(monkeypatch):
    monkeypatch.delenv("SKILL_FORGE_LLM_API_KEY", raising=False)
    monkeypatch.delenv("SKILL_FORGE_LLM_MODEL", raising=False)
    monkeypatch.delenv("SKILL_FORGE_LLM_BASE_URL", raising=False)


def _write_eval_case(
    path: Path,
    *,
    case_id: str = "basic",
    skill: str,
    forbidden_phrases: list[str] | None = None,
) -> Path:
    forbidden = forbidden_phrases if forbidden_phrases is not None else ["looks good"]
    path.write_text(
        "\n".join(
            [
                f"id: {case_id}",
                f"skill: {skill}",
                "input:",
                "  request: Review this implementation.",
                "assertions:",
                "  required_sections:",
                "    - When to use",
                "    - Workflow",
                "  required_constraints:",
                "    - Quality gates",
                "  forbidden_phrases:",
                *[f"    - {phrase}" for phrase in forbidden],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def _write_experience_source_package(
    output_dir: Path,
    name: str,
    *,
    generated_at: str,
    assertion_message: str = "Missing required section: Findings",
) -> Path:
    package_dir = output_dir / name
    package_dir.mkdir(parents=True)
    (package_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Sample skill.\n---\n\n# {name}\n\n## Findings\n\nDetails.\n",
        encoding="utf-8",
    )
    provenance = GenerationProvenanceMetadata(
        generated_at=generated_at,
        skill_name=name,
        requirement_text="Java bug investigation skill",
        target_platform="opencode",
        language="zh-CN",
        task_type="bug-investigation",
        quality_score=70,
        quality_status="valid_with_warnings",
        content_quality=ContentQualityMetrics(
            workflow_specificity=0.2,
            constraint_verifiability=0.8,
            quality_gate_clarity=0.9,
        ),
    )
    (package_dir / "skill-forge.json").write_text(provenance.model_dump_json(indent=2), encoding="utf-8")
    report = SkillEvalReport(
        skill_name=name,
        total=1,
        passed=0,
        failed=1,
        results=[
            SkillEvalCaseResult(
                case_id="case-1",
                passed=False,
                assertions=[
                    SkillEvalAssertionResult(
                        passed=False,
                        assertion="required_sections",
                        message=assertion_message,
                    )
                ],
            )
        ],
    )
    (package_dir / "eval-report.json").write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return package_dir


def test_help_lists_init_command() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.output


def test_init_creates_workspace(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"

    result = runner.invoke(app, ["init", "--home", str(home)])

    assert result.exit_code == 0
    assert (home / "config.yaml").is_file()
    assert (home / "db" / "skill_forge.sqlite").is_file()
    for name in ("corpus", "drafts", "output", "blueprints", "index", "logs", "db"):
        assert (home / name).is_dir()

    assert {
        "sources",
        "documents",
        "skill_examples",
        "skill_patterns",
        "drafts",
    }.issubset(list_tables(home / "db" / "skill_forge.sqlite"))


def test_init_preserves_existing_config(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    config = home / "config.yaml"
    config.parent.mkdir(parents=True)
    config.write_text("custom: true\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--home", str(home)])

    assert result.exit_code == 0
    assert config.read_text(encoding="utf-8") == "custom: true\n"
    assert "preserved" in result.output


def test_create_generates_skill_package(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    assert result.exit_code == 0
    skill_md = home / "output" / "java-bug-investigation" / "SKILL.md"
    assert skill_md.is_file()
    assert "Skill package generated" in result.output
    assert "Quality: 100/100" in result.output
    assert "java-bug-investigation" in result.output


def test_create_writes_generation_provenance_metadata(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    metadata_path = home / "output" / "java-bug-investigation" / "skill-forge.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert metadata["schema_version"] == 1
    assert metadata["skill_name"] == "java-bug-investigation"
    assert metadata["requirement_text"] == "Java 存量代码 bug 定位 skill"
    assert metadata["target_platform"] == "opencode"
    assert metadata["language"] == "zh-CN"
    assert metadata["task_type"] == "bug-investigation"
    assert metadata["blueprint_id"] == "bug-investigation"
    assert metadata["blueprint_source"] == "builtin"
    assert metadata["llm_enabled"] is False
    assert metadata["llm_mode"] == "auto"
    assert metadata["llm_selection"] == "auto-fallback"
    assert "Missing LLM configuration" in metadata["llm_fallback_reason"]
    assert metadata["applied_experience_rule_ids"] == []
    assert metadata["quality_score"] == 100
    assert metadata["quality_status"] == "valid"
    assert "content_quality" in metadata
    assert metadata["references"] == ["references/diagnosis-checklist.md"]
    assert "project_context_summary" not in metadata


def test_experience_derive_command_rebuilds_local_rules(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    output_dir = home / "output"
    _write_experience_source_package(output_dir, "pkg-a", generated_at="2026-05-31T00:00:00Z")
    _write_experience_source_package(output_dir, "pkg-b", generated_at="2026-05-31T01:00:00Z")
    _write_experience_source_package(output_dir, "pkg-c", generated_at="2026-05-31T02:00:00Z")

    result = runner.invoke(app, ["experience", "derive", "--home", str(home)])

    assert result.exit_code == 0
    assert "Experience derivation" in result.output
    assert "Derived rules" in result.output
    assert list((home / "experience").glob("*.json"))


def test_create_records_and_shows_applied_experience_rules(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    experience_dir = home / "experience"
    experience_dir.mkdir(parents=True)
    rule = ExperienceRule(
        id="experience-123",
        task_type="bug-investigation",
        language="zh-CN",
        target_platform="opencode",
        priority=80,
        rule_text="For bug-investigation, confirm logs before code changes.",
        workflow_guidance=["Confirm logs before code changes."],
        constraint_guidance=["Do not change code before logs are reviewed."],
        quality_gate_guidance=["Pass only when logs are linked to the root cause."],
        evidence=[],
        derived_at="2026-05-31T00:00:00Z",
    )
    (experience_dir / f"{rule.id}.json").write_text(rule.model_dump_json(indent=2), encoding="utf-8")

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    metadata = json.loads((home / "output" / "java-bug-investigation" / "skill-forge.json").read_text(encoding="utf-8"))
    show_result = runner.invoke(app, ["show", "java-bug-investigation", "--home", str(home)])

    assert result.exit_code == 0
    assert metadata["applied_experience_rule_ids"] == [rule.id]
    assert "Applied experience rules" in show_result.output
    assert rule.id in show_result.output


def test_create_output_dir_overrides_configured_output_directory(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    output_dir = tmp_path / "skills"

    result = runner.invoke(
        app,
        ["create", "Java 存量代码 bug 定位 skill", "--home", str(home), "--output-dir", str(output_dir)],
    )

    assert result.exit_code == 0
    assert (output_dir / "java-bug-investigation" / "SKILL.md").is_file()
    assert not (home / "output" / "java-bug-investigation").exists()


def test_create_without_llm_does_not_require_llm_configuration(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--home", str(home)])

    assert result.exit_code == 0
    assert (home / "output" / "custom-skill" / "SKILL.md").is_file()


def test_create_without_llm_uses_configured_llm_by_default(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    client = FakeLLMClient(
        '{"description": "Use this skill for release readiness checks.", '
        '"workflow": ["Confirm release scope", "Check rollout risks"]}'
    )
    monkeypatch.setenv("SKILL_FORGE_LLM_API_KEY", "test-key")
    monkeypatch.setenv("SKILL_FORGE_LLM_MODEL", "test-model")
    monkeypatch.setattr(cli_module.OpenAICompatibleLLMClient, "from_env", lambda: client)

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--home", str(home)])

    metadata = json.loads((home / "output" / "custom-skill" / "skill-forge.json").read_text(encoding="utf-8"))
    content = (home / "output" / "custom-skill" / "SKILL.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "Use this skill for release readiness checks." in content
    assert metadata["llm_enabled"] is True
    assert metadata["llm_mode"] == "auto"
    assert metadata["llm_selection"] == "auto-selected"
    assert metadata["llm_generated_fields"] == ["workflow"]


def test_create_with_llm_refines_requirement(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    monkeypatch.setattr(
        cli_module.OpenAICompatibleLLMClient,
        "from_env",
        lambda: FakeLLMClient(
            '{"description": "Use this skill for release readiness checks. Do not use it for unrelated implementation work.", '
            '"workflow": ["Confirm release scope", "Check rollout risks"]}'
        ),
    )

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--llm", "--home", str(home)])

    skill_md = home / "output" / "custom-skill" / "SKILL.md"
    assert result.exit_code == 0
    assert "Quality: 100/100" in result.output
    content = skill_md.read_text(encoding="utf-8")
    assert "Use this skill for release readiness checks." in content
    assert "Confirm release scope" in content


def test_create_with_llm_uses_blueprint_before_generation(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    client = FakeLLMClient(
        '{"workflow": ["Inspect the Java stack trace before changing code"], '
        '"quality_gates": ["Pass when root cause evidence is linked to the failing Java path"]}'
    )
    monkeypatch.setattr(cli_module.OpenAICompatibleLLMClient, "from_env", lambda: client)

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--llm", "--home", str(home)])

    metadata = json.loads((home / "output" / "java-bug-investigation" / "skill-forge.json").read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert client.seen_requirements[0].applied_blueprint_id == "bug-investigation"
    assert client.seen_requirements[0].workflow
    assert metadata["llm_generated_fields"] == ["quality_gates", "workflow"]
    assert metadata["llm_fallback_fields"] == []
    assert metadata["content_quality"]["workflow_specificity"] >= 0


def test_create_with_llm_uses_project_context_before_generation(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    project = tmp_path / "project"
    project.mkdir()
    (project / "README.md").write_text("This project uses OpenSpec changes and pytest tests.", encoding="utf-8")
    client = FakeLLMClient("{}")
    monkeypatch.setattr(cli_module.OpenAICompatibleLLMClient, "from_env", lambda: client)

    result = runner.invoke(
        app,
        ["create", "整理团队发布流程 skill", "--llm", "--project", str(project), "--home", str(home)],
    )

    assert result.exit_code == 0
    assert any("Project constraint:" in constraint for constraint in client.seen_requirements[0].constraints)


def test_create_with_llm_records_used_retrieval_augmentation(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    retrieval_context = GenerationRetrievalContext(
        used=True,
        source_names=["Bug Investigation#1"],
        workflow_patterns=["Inspect logs before editing code"],
        constraint_patterns=["Do not change code before evidence is documented"],
        quality_gate_patterns=["Pass when evidence links logs to code"],
    )
    monkeypatch.setattr(
        cli_module,
        "_build_generation_retrieval_context",
        lambda **kwargs: retrieval_context,
    )
    monkeypatch.setattr(
        cli_module.OpenAICompatibleLLMClient,
        "from_env",
        lambda: FakeLLMClient('{"workflow": ["Inspect application logs before editing code"]}'),
    )

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--llm", "--home", str(home)])

    metadata = json.loads((home / "output" / "java-bug-investigation" / "skill-forge.json").read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert metadata["retrieval_augmented"] is True
    assert metadata["retrieval_augmentation_reason"] is None
    assert metadata["retrieval_reference_names"] == ["Bug Investigation#1"]


def test_create_with_llm_records_skipped_retrieval_augmentation(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    monkeypatch.setattr(
        cli_module,
        "_build_generation_retrieval_context",
        lambda **kwargs: GenerationRetrievalContext(skipped_reason="empty-corpus"),
    )
    monkeypatch.setattr(
        cli_module.OpenAICompatibleLLMClient,
        "from_env",
        lambda: FakeLLMClient('{"workflow": ["Confirm release scope"]}'),
    )

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--llm", "--home", str(home)])

    metadata = json.loads((home / "output" / "custom-skill" / "skill-forge.json").read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert metadata["retrieval_augmented"] is False
    assert metadata["retrieval_augmentation_reason"] == "empty-corpus"
    assert metadata["retrieval_reference_names"] == []


def test_create_no_llm_does_not_build_retrieval_context(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"

    def fail_retrieval_context(**kwargs):
        raise AssertionError("retrieval augmentation should not run")

    monkeypatch.setattr(cli_module, "_build_generation_retrieval_context", fail_retrieval_context)

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--no-llm", "--home", str(home)])

    metadata = json.loads((home / "output" / "custom-skill" / "skill-forge.json").read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert metadata["retrieval_augmented"] is False
    assert metadata["retrieval_augmentation_reason"] is None


def test_create_with_llm_reports_missing_configuration(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--llm", "--home", str(home)])

    assert result.exit_code == 1
    assert "LLM configuration error" in result.output
    assert "SKILL_FORGE_LLM_API_KEY" in result.output


def test_create_with_llm_reports_unavailable_provider(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"

    class UnavailableLLMClient(FakeLLMClient):
        def check_availability(self, *, timeout_seconds: float = 1.0) -> None:
            raise cli_module.LLMAvailabilityError("provider unavailable")

    monkeypatch.setenv("SKILL_FORGE_LLM_API_KEY", "test-key")
    monkeypatch.setenv("SKILL_FORGE_LLM_MODEL", "test-model")
    monkeypatch.setattr(cli_module.OpenAICompatibleLLMClient, "from_env", lambda: UnavailableLLMClient("{}"))

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--llm", "--home", str(home)])

    assert result.exit_code == 1
    assert "LLM availability error" in result.output
    assert "provider unavailable" in result.output


def test_create_no_llm_bypasses_detection(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    monkeypatch.setenv("SKILL_FORGE_LLM_API_KEY", "test-key")
    monkeypatch.setenv("SKILL_FORGE_LLM_MODEL", "test-model")

    def fail_from_env():
        raise AssertionError("LLM client should not be constructed")

    monkeypatch.setattr(cli_module.OpenAICompatibleLLMClient, "from_env", fail_from_env)

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--no-llm", "--home", str(home)])

    metadata = json.loads((home / "output" / "custom-skill" / "skill-forge.json").read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert metadata["llm_enabled"] is False
    assert metadata["llm_mode"] == "disabled"
    assert metadata["llm_selection"] == "disabled"
    assert metadata["llm_fallback_reason"] is None


def test_create_rejects_conflicting_llm_flags(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["create", "整理团队发布流程 skill", "--llm", "--no-llm", "--home", str(tmp_path / "home")],
    )

    assert result.exit_code == 1
    assert "Conflicting options" in result.output


def test_create_with_llm_falls_back_on_bad_response(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"
    monkeypatch.setattr(cli_module.OpenAICompatibleLLMClient, "from_env", lambda: FakeLLMClient("not-json"))

    result = runner.invoke(app, ["create", "整理团队发布流程 skill", "--llm", "--home", str(home)])

    metadata = json.loads((home / "output" / "custom-skill" / "skill-forge.json").read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert (home / "output" / "custom-skill" / "SKILL.md").is_file()
    assert metadata["llm_enabled"] is True
    assert metadata["llm_mode"] == "force"
    assert metadata["llm_selection"] == "forced"
    assert "not valid JSON" in metadata["llm_fallback_reason"]
    assert metadata["llm_fallback_fields"]


def test_create_rejects_llm_with_interactive(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["create", "Java bug 定位 skill", "--interactive", "--llm", "--home", str(tmp_path / "home")],
    )

    assert result.exit_code == 1
    assert "only supported for non-interactive create" in result.output


def test_create_succeeds_with_quality_warnings(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"

    def validate_with_warning(self, skill_path, attachment_paths=None):
        return ValidationResult(
            ok=True,
            warnings=[ValidationIssue(level="warning", code="missing_section", message="Recommended section is missing")],
        )

    monkeypatch.setattr(SkillValidator, "validate", validate_with_warning)

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    assert result.exit_code == 0
    assert "Quality: 95/100" in result.output
    assert "valid_with_warnings" in result.output
    assert "missing_section" in result.output
    assert "Suggested fixes" in result.output
    assert "Add the missing recommended section" in result.output


def test_create_fails_with_quality_errors(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"

    def validate_with_error(self, skill_path, attachment_paths=None):
        return ValidationResult(
            ok=False,
            errors=[ValidationIssue(level="error", code="missing_skill_md", message="Missing SKILL.md")],
        )

    monkeypatch.setattr(SkillValidator, "validate", validate_with_error)

    result = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    assert result.exit_code == 1
    assert "Quality: 70/100" in result.output
    assert "Generated Skill package is invalid" in result.output
    assert "missing_skill_md" in result.output
    assert "Suggested fixes" in result.output
    assert "Add a SKILL.md file" in result.output


def test_non_interactive_create_help_remains_available() -> None:
    result = runner.invoke(app, ["create", "--help"])

    assert result.exit_code == 0
    assert "--interactive" in result.output


def test_create_fails_when_package_exists(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    first = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    second = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    assert first.exit_code == 0
    assert second.exit_code == 1
    assert "Skill package already exists" in second.output


def test_interactive_create_generates_skill_and_saves_draft(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "skill-forge-home"

    monkeypatch.setattr(QuestionaryPromptAdapter, "text", lambda self, message, default="": default)
    monkeypatch.setattr(QuestionaryPromptAdapter, "multiline", lambda self, message, default: default)

    result = runner.invoke(app, ["create", "Java bug 定位 skill", "--interactive", "--home", str(home)])

    drafts = list((home / "drafts").glob("*.json"))
    assert result.exit_code == 0
    assert drafts
    assert "Interactive draft" in result.output
    assert (home / "output" / "java-bug-investigation" / "SKILL.md").is_file()


def test_resume_fails_for_missing_draft(tmp_path: Path) -> None:
    result = runner.invoke(app, ["resume", "missing", "--home", str(tmp_path / "home")])

    assert result.exit_code == 1
    assert "Draft not found" in result.output


def test_validate_command_succeeds_for_generated_package(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    create = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    skill_dir = home / "output" / "java-bug-investigation"

    result = runner.invoke(app, ["validate", str(skill_dir)])

    assert create.exit_code == 0
    assert result.exit_code == 0
    assert "Skill package is valid" in result.output
    assert "Suggested fixes" not in result.output


def test_validate_command_fails_for_invalid_package(tmp_path: Path) -> None:
    result = runner.invoke(app, ["validate", str(tmp_path / "missing")])

    assert result.exit_code == 1
    assert "Skill package is invalid" in result.output
    assert "missing_directory" in result.output
    assert "Suggested fixes" in result.output
    assert "Create the Skill package directory" in result.output


def test_list_command_lists_generated_skills(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    create = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    result = runner.invoke(app, ["list", "--home", str(home)])

    assert create.exit_code == 0
    assert result.exit_code == 0
    assert "Generated Skills" in result.output
    assert "java-bug-investigation" in result.output


def test_list_command_reports_empty_library(tmp_path: Path) -> None:
    result = runner.invoke(app, ["list", "--home", str(tmp_path / "home")])

    assert result.exit_code == 0
    assert "No generated Skill packages found" in result.output


def test_show_command_displays_generated_skill_metadata(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    result = runner.invoke(app, ["show", "java-bug-investigation", "--home", str(home)])

    assert result.exit_code == 0
    assert "Generated Skill: java-bug-investigation" in result.output
    assert "SKILL.md" in result.output
    assert "References" in result.output
    assert "Blueprint" in result.output
    assert "bug-investigation" in result.output
    assert "Quality" in result.output
    assert "Content quality" in result.output
    assert "workflow=" in result.output


def test_show_command_displays_eval_summary_when_present(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    eval_case = _write_eval_case(tmp_path / "case.yaml", skill="java-bug-investigation")
    eval_result = runner.invoke(app, ["eval", "java-bug-investigation", "--case", str(eval_case), "--home", str(home)])

    result = runner.invoke(app, ["show", "java-bug-investigation", "--home", str(home)])

    assert eval_result.exit_code == 0
    assert result.exit_code == 0
    assert "Eval summary" in result.output
    assert "1/1 passed, 0 failed" in result.output


def test_show_command_fails_for_missing_generated_skill(tmp_path: Path) -> None:
    result = runner.invoke(app, ["show", "missing", "--home", str(tmp_path / "home")])

    assert result.exit_code == 1
    assert "Generated Skill package not found" in result.output


def test_eval_command_runs_single_case_and_writes_report(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    create = runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    eval_case = _write_eval_case(tmp_path / "case.yaml", skill="java-bug-investigation")

    result = runner.invoke(app, ["eval", "java-bug-investigation", "--case", str(eval_case), "--home", str(home)])

    report = json.loads((home / "output" / "java-bug-investigation" / "eval-report.json").read_text(encoding="utf-8"))
    assert create.exit_code == 0
    assert result.exit_code == 0
    assert "Eval: 1/1 passed" in result.output
    assert "Eval results" in result.output
    assert report["total"] == 1
    assert report["passed"] == 1


def test_eval_command_runs_batch_cases(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    _write_eval_case(cases_dir / "b.yml", case_id="b", skill="java-bug-investigation")
    _write_eval_case(cases_dir / "a.yaml", case_id="a", skill="java-bug-investigation")

    result = runner.invoke(app, ["eval", "java-bug-investigation", "--cases", str(cases_dir), "--home", str(home)])

    assert result.exit_code == 0
    assert "Eval: 2/2 passed" in result.output
    assert "a" in result.output
    assert "b" in result.output


def test_eval_command_exits_nonzero_for_failed_case(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    eval_case = _write_eval_case(
        tmp_path / "case.yaml",
        skill="java-bug-investigation",
        forbidden_phrases=["Java"],
    )

    result = runner.invoke(app, ["eval", "java-bug-investigation", "--case", str(eval_case), "--home", str(home)])

    assert result.exit_code == 1
    assert "failed" in result.output
    assert "Forbidden phrase found: Java" in result.output


def test_eval_command_fails_for_missing_generated_skill(tmp_path: Path) -> None:
    eval_case = _write_eval_case(tmp_path / "case.yaml", skill="missing")

    result = runner.invoke(app, ["eval", "missing", "--case", str(eval_case), "--home", str(tmp_path / "home")])

    assert result.exit_code == 1
    assert "Generated Skill package not found" in result.output


def test_diff_command_compares_generated_skill_md(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    runner.invoke(app, ["create", "Python 代码审查 skill", "--home", str(home)])

    result = runner.invoke(app, ["diff", "java-bug-investigation", "code-review", "--home", str(home)])

    assert result.exit_code == 0
    assert "--- java-bug-investigation/SKILL.md" in result.output
    assert "+++ code-review/SKILL.md" in result.output


def test_diff_command_reports_no_differences(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    output_dir = home / "output"
    duplicate = output_dir / "java-bug-copy"
    duplicate.mkdir()
    duplicate.joinpath("SKILL.md").write_text(
        output_dir.joinpath("java-bug-investigation", "SKILL.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    duplicate.joinpath("skill-forge.json").write_text(
        output_dir.joinpath("java-bug-investigation", "skill-forge.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["diff", "java-bug-investigation", "java-bug-copy", "--home", str(home)])

    assert result.exit_code == 0
    assert "No differences found" in result.output


def test_diff_command_fails_for_missing_generated_skill(tmp_path: Path) -> None:
    result = runner.invoke(app, ["diff", "left", "missing", "--home", str(tmp_path / "home")])

    assert result.exit_code == 1
    assert "Generated Skill package not found" in result.output


def test_install_command_installs_project_opencode_skill(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    project = tmp_path / "project"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])

    result = runner.invoke(
        app,
        [
            "install",
            "java-bug-investigation",
            "--target",
            "opencode",
            "--scope",
            "project",
            "--home",
            str(home),
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 0
    assert (project / ".opencode" / "skills" / "java-bug-investigation" / "SKILL.md").is_file()
    assert "Skill installed" in result.output


def test_install_command_fails_for_missing_source(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "install",
            "missing",
            "--target",
            "opencode",
            "--scope",
            "project",
            "--home",
            str(tmp_path / "home"),
            "--project",
            str(tmp_path / "project"),
        ],
    )

    assert result.exit_code == 1
    assert "Generated Skill package not found" in result.output


def test_install_command_fails_when_destination_exists_without_force(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    project = tmp_path / "project"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    args = [
        "install",
        "java-bug-investigation",
        "--target",
        "opencode",
        "--scope",
        "project",
        "--home",
        str(home),
        "--project",
        str(project),
    ]

    first = runner.invoke(app, args)
    second = runner.invoke(app, args)

    assert first.exit_code == 0
    assert second.exit_code == 1
    assert "Installed Skill already exists" in second.output


def test_install_command_force_overwrites_existing_destination(tmp_path: Path) -> None:
    home = tmp_path / "skill-forge-home"
    project = tmp_path / "project"
    runner.invoke(app, ["create", "Java 存量代码 bug 定位 skill", "--home", str(home)])
    args = [
        "install",
        "java-bug-investigation",
        "--target",
        "opencode",
        "--scope",
        "project",
        "--home",
        str(home),
        "--project",
        str(project),
    ]
    first = runner.invoke(app, args)
    destination = project / ".opencode" / "skills" / "java-bug-investigation"
    (destination / "old.txt").write_text("old", encoding="utf-8")

    second = runner.invoke(app, [*args, "--force"])

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert not (destination / "old.txt").exists()
